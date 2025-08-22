"""
speechDescriptors
==============


.. autosummary::
    :toctree: generated/

    get_speech_descriptors
        
"""

import parselmouth
import librosa
import pandas as pd
import numpy as np

__all__ = [
    "get_speech_descriptors"
]

def createDataframe(speech_file):
    df = pd.read_csv(speech_file, header=None, names=["onset_sec", "pitch_est", "duration", "word"])
    return df

def get_speech_descriptors(audio, df, speaker_type="female"):    
   # df is a dict of DataFrames — get first part
    df = list(df.values())[0]
    print("Available columns:", list(df.columns))  # helpful debug output

    df = df[['ONSET_SEC', 'OFFSET_SEC', 'AVG PITCH IN HZ', 'DURATION', 'WORD', 'meanSpecCent']]                
    # df = createDataframe(speech)    
    snd = parselmouth.Sound(audio)

    # Pitch analysis parameters (rows 6-9 in sheet)
    # time_step = 0.0025  # pitch per phoneme
    time_step = 0.01 # pitch per word
    pitch_floor = 75
    pitch_ceiling = 600
    octave_cost = 0.01
    octave_jump_cost = 0.35
    voicing_threshold = 0.45
    silence_threshold = 0.03

    # For pulses and jitter
    min_period = 1.0 / pitch_ceiling  # shortest period = highest pitch
    max_period = 1.0 / pitch_floor    # longest period = lowest pitch
    maximum_period_factor = 1.3 # Maximum period factor: If the duration of a period 
                                # is larger than 1.3 times the previous period, it is 
                                # excluded from the jitter calculation.

    # For shimmer
    max_amplitude_factor = 1.6 # default in Praat for shimmer


    # Resonance/formant ceiling based on speaker type
    resonance_ceiling = {
        "male": 5000,
        "female": 5500,
        "child": 8000
    }.get(speaker_type.lower(), 5500)  # default = female

    # Generate pitch object using custom parameters
    pitch = snd.to_pitch(        
        parselmouth.Sound.ToPitchMethod.AC,
        time_step,   # time_step (required, just make it small)
        pitch_floor,      # pitch_floor
        pitch_ceiling,     # pitch_ceiling
        octave_cost,    # octave_cost
        octave_jump_cost,    # octave_jump_cost
        voicing_threshold,    # voicing_threshold
        silence_threshold     # silence_threshold        
    )    

    # Extract voiced pitch values and calculate pitch range
    pitch_values = pitch.selected_array['frequency']
    voiced = pitch_values[pitch_values > 0]
    pitch_range = voiced.max() - voiced.min() if len(voiced) else 0

    # Intensity
    intensity = snd.to_intensity()

    # Formant extraction
    formant = snd.to_formant_burg(
        time_step=time_step,
        max_number_of_formants=5,
        maximum_formant=resonance_ceiling
    )

    # # Pulses - GLOBAL maybe add later
    # pulses = parselmouth.praat.call([snd, pitch], "To PointProcess (cc)")

    # Shimmer and Jitter        
    point_process = parselmouth.praat.call(snd, "To PointProcess (periodic, cc)", pitch_floor, pitch_ceiling)

    descriptors = []

    for i in df.index:
        onset = df.at[i, "ONSET_SEC"]
        duration = df.at[i, "DURATION"]
        offset = df.at[i, "OFFSET_SEC"]
        t_values = np.arange(onset, offset, 0.01)
        
        # Pitch per row
        pitch_segment = [pitch.get_value_at_time(t) for t in t_values]
        voiced_segment = [p for p in pitch_segment if p and p > 0]
        mean_pitch = np.mean(voiced_segment) if voiced_segment else 0
        
        # Intensity per row
        intensity_segment = [intensity.get_value(t) for t in t_values]
        intensity_values = [v for v in intensity_segment if v and v > 0]
        mean_intensity = np.mean(intensity_values) if intensity_values else 0

        # Formants: mean of first 3, per row
        f1_vals = [formant.get_value_at_time(1, t) for t in t_values if formant.get_value_at_time(1, t) > 0]
        f2_vals = [formant.get_value_at_time(2, t) for t in t_values if formant.get_value_at_time(2, t) > 0]
        f3_vals = [formant.get_value_at_time(3, t) for t in t_values if formant.get_value_at_time(3, t) > 0]
        mean_f1 = np.mean(f1_vals) if f1_vals else 0
        mean_f2 = np.mean(f2_vals) if f2_vals else 0
        mean_f3 = np.mean(f3_vals) if f3_vals else 0        

        # Jitter (local)
        jitter_local = parselmouth.praat.call(point_process, "Get jitter (local)", onset, offset, min_period, 
                                              max_period, maximum_period_factor)

        jitter_percent = jitter_local * 100 if jitter_local else 0

        # Shimmer (local), then convert to percent
        shimmer_local = parselmouth.praat.call([snd, point_process], "Get shimmer (local)",
            onset, offset, min_period, max_period, maximum_period_factor, max_amplitude_factor
        )
        shimmer_percent = shimmer_local * 100 if shimmer_local else 0

        # Extract segment
        seg = snd.extract_part(from_time=onset, to_time=offset, preserve_times=True)

        # Create PowerCepstrogram
        pcg = parselmouth.praat.call(
            seg, "To PowerCepstrogram...",
            pitch_floor,        # e.g. 75.0
            time_step,          # e.g. 0.01
            resonance_ceiling,  # e.g. 5500.0
            50                  # pre-emphasis from Hz
        )

        # Get CPPS (dB)
        cpps = parselmouth.praat.call(
            pcg, "Get CPPS...",
            "yes",      # subtract trend
            0.05,       # time smoothing window (seconds)
            0.001,      # quefrency smoothing window (seconds)
            pitch_floor, pitch_ceiling,  # search range for peak
            0.05,        # peak search tolerance (Hz)
            "parabolic",
            0.001, 0.05,  # trend line quefrency range (seconds)
            "straight",
            "robust slow"
        )

        y = seg.values[0]  # Parselmouth Sound to numpy (mono)
        sr = int(seg.sampling_frequency)

        # Compute spectral centroid (Hz)
        spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        mean_spec_centroid = float(np.mean(spec_centroid))

        # Get magnitude spectrogram
        S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512)) # PASS THIS?!?!

        # Calculate spectral flux
        spec_flux = featureSpectralFlux(S, sr)
        mean_spec_flux = float(np.mean(spec_flux))

        descriptors.append((mean_pitch, mean_intensity, mean_f1, mean_f2, mean_f3, 
                            jitter_local, jitter_percent, shimmer_local, shimmer_percent, cpps, mean_spec_centroid, mean_spec_flux))


    # Add descriptors to the original DataFrame
    df[["pitch", "intensity", "mean_f1", "mean_f2", "mean_f3", 
        "jitter_local", "jitter_percent", "shimmer_local", 
        "shimmer_percent", "cpps", "mean_spec_centroid", "mean_spec_flux"]] = pd.DataFrame(descriptors, index=df.index)
    
    return df
    

## computes the spectral flux from the magnitude spectrum
#
#    @param X: spectrogram (dimension FFTLength X Observations)
#    @param f_s: sample rate of audio data
#
#    @return vsf: spectral flux
def featureSpectralFlux(X, f_s):

    isSpectrum = X.ndim == 1
    if isSpectrum:
        X = np.expand_dims(X, axis=1)

    # difference spectrum (set first diff to zero)
    X = np.c_[X[:, 0], X]

    afDeltaX = np.diff(X, 1, axis=1)

    # flux
    vsf = np.sqrt((afDeltaX**2).sum(axis=0)) / X.shape[0]

    return np.squeeze(vsf) if isSpectrum else vsf

    # # Uncomment if you want globals as a separate df
    # # Store global pitch metrics as metadata     
    # globals_df = pd.DataFrame([{
    #     "pitch_floor": pitch_floor,
    #     "pitch_ceiling": pitch_ceiling,
    #     "pitch_range": pitch_range,
    #     "octave_cost": octave_cost,
    #     "octave_jump_cost": octave_jump_cost,
    #     "voicing_threshold": voicing_threshold,
    #     "silence_threshold": silence_threshold,
    #     "formant_ceiling": resonance_ceiling,
    #     "time_step": time_step,
    #     "speaker_type": speaker_type
    # }])

    # # Return both dataframes in a dict
    # return {
    #     "globals": globals_df,
    #     "per_word": df 
    # }
    



# Pitch - built
# Pitch Range - built
# Pitch floor (Hz) - built
# Pitch ceiling (Hz) - built
# “octave jump cost” - built
# “octave cost” - built
# “voicing threshold” - built
# “silence threshold” - built
# Intensity - built
# Formant - built
# Jitter - built
# Shimmer - built
# CPPS (Soft Central Peak Prominence) - built
# GNE (glottal-to-noise excitation ratio) - segfault!
# AVQI (Acoustic Voice Quality Index) - NEED PRAAT SCRIPT
# Spectral Centroid - built
# Spectral Flux - kinda built...check ntft spec, pass in?