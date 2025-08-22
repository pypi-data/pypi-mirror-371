"""
dataCompilation
===============




.. autosummary::
    :toctree: generated/
    
    data_compilation
"""

import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.patches import Patch
from pyampact.performance import estimate_perceptual_parameters
from pyampact.alignmentUtils import f0_est_weighted_sum_spec
from pyampact.symbolic import Score

__all__ = [
    "data_compilation",
    "export_selected_columns",
    "visualise_alignment_from_nmat"                                                 
]


def data_compilation(y, original_sr, hop_length, winms, tsr, spec, nmat, piece, audio_file_path, output_path="output"):
    """
    This function takes the results of the alignment and the note matrix and compiles the data into a JSON object
    that can be used to insert the audio analysis into the score.

    Parameters
    ----------
    nmat : np.ndarray
        The note matrix containing information about notes, including their timing and duration.
    
    hop_length : int
        Hop length
    
    spec : np.ndarray
        Spec (check type and fill out)

    audio_file : str
        The path to the audio file associated with the performance data.

    piece : Score
        An instantiation of the original Score object containing the data input for the musical piece.

    output_path : str, optional
        The file path for the output MEI file. Defaults to './output'.

    Returns
    -------            
    nmat : The note matrix with performance data appended.
    json_data : A JSON object containing the compiled data.
    xml_data : XML data representing the MEI output.

    """

    all_note_vals = []
    all_note_ids = []
    fft_len = int(2**np.round(np.log(winms/1000*tsr)/np.log(2)))
    for key, df in nmat.items():
        df = df.drop(columns=['MEASURE', 'ONSET', 'DURATION', 'PART', 'MIDI'])

        midiList = np.array(nmat[key]['MIDI'])
        note_vals = []
        note_ids = []
        is_monophonic = len(nmat) == 1  # Only one part = monophonic or speech

        for i in range(len(df)):
            onset = df['ONSET_SEC'].iloc[i]
            offset = df['OFFSET_SEC'].iloc[i]
            midi = midiList[i]            

            if is_monophonic:
                try:          
                                                  
                    # Slice audio
                    y_seg = y[int(onset * original_sr):int(offset * original_sr)]

                    # Estimate f0 and RMS
                    f0, voiced_flag, voiced_probs = librosa.pyin(
                        y_seg,
                        fmin=librosa.note_to_hz('C2'),
                        fmax=librosa.note_to_hz('C7'),
                        sr=original_sr
                    )
                    pwr = librosa.feature.rms(y=y_seg).flatten()
                    
                    # time and frequency axes
                    t = librosa.times_like(pwr, sr=original_sr)
                    xf = librosa.fft_frequencies(sr=original_sr, n_fft=fft_len)
                    
                    M = spec

                    # Estimate parameters
                    note_vals.append(estimate_perceptual_parameters(
                        f0, pwr, M, original_sr, 256, 1
                    ))

                except Exception as e:                    
                    note_vals.append({
                        'f0_vals': np.nan,
                        'ppitch': (np.nan, np.nan),
                        'jitter': np.nan,
                        'vibrato_depth': np.nan,
                        'vibrato_rate': np.nan,
                        'pwr_vals': np.nan,
                        'shimmer': np.nan,
                        'spec_centroid': np.nan,
                        'spec_bandwidth': np.nan,
                        'spec_contrast': np.nan,
                        'spec_flatness': np.nan,
                        'spec_rolloff': np.nan
                    })

            else:
                freqs, times, D = librosa.reassigned_spectrogram(
                    y=y, sr=original_sr, hop_length=hop_length)
                f0, pwr, t, M_seg, xf = f0_est_weighted_sum_spec(
                    onset, offset, midi, freqs, D, original_sr
                )
                note_vals.append(estimate_perceptual_parameters(
                    f0, pwr, M_seg, original_sr, 256, 1
                ))

            note_ids.append(df.index[i])

        all_note_vals.append(note_vals)
        all_note_ids.append(note_ids)

    loc = 0  # This stays for post-processing


    for key, df in nmat.items():
        df['f0Vals'] = [all_note_vals[loc][i]['f0_vals'] for i in range(len(df))]
        df['meanf0'] = [np.mean(vals) for vals in df['f0Vals']]

        df['ppitch1'] = [all_note_vals[loc][i]['ppitch'][0] for i in range(len(df))]
        df['ppitch2'] = [all_note_vals[loc][i]['ppitch'][1] for i in range(len(df))]
        df['jitter'] = [all_note_vals[loc][i]['jitter'] for i in range(len(df))]

        df['vibratoDepth'] = [all_note_vals[loc][i]['vibrato_depth'] for i in range(len(df))]
        df['vibratoRate'] = [all_note_vals[loc][i]['vibrato_rate'] for i in range(len(df))]

        df['pwrVals'] = [all_note_vals[loc][i]['pwr_vals'] for i in range(len(df))]
        df['meanPwr'] = [np.mean(vals) for vals in df['pwrVals']]
        df['shimmer'] = [all_note_vals[loc][i]['shimmer'] for i in range(len(df))]

        df['specCentVals'] = [all_note_vals[loc][i]['spec_centroid'] for i in range(len(df))]
        df['meanSpecCent'] = [np.mean(vals) for vals in df['specCentVals']]

        df['specBandwidthVals'] = [all_note_vals[loc][i]['spec_bandwidth'] for i in range(len(df))]
        df['meanSpecBandwidth'] = [np.mean(vals) for vals in df['specBandwidthVals']]

        df['specContrastVals'] = [all_note_vals[loc][i]['spec_contrast'] for i in range(len(df))]
        df['meanSpecContrast'] = [np.mean(vals) for vals in df['specContrastVals']]

        df['specFlatnessVals'] = [all_note_vals[loc][i]['spec_flatness'] for i in range(len(df))]
        df['meanSpecFlatness'] = [np.mean(vals) for vals in df['specFlatnessVals']]

        df['specRolloffVals'] = [all_note_vals[loc][i]['spec_rolloff'] for i in range(len(df))]
        df['meanSpecRolloff'] = [np.mean(vals) for vals in df['specRolloffVals']]

        loc += 1
        
    
    def convert_nmat_for_export(nmat):
        """
        Converts columns with list values into stringified versions for export (e.g., MEI, CSV, JSON).

        Parameters
        ----------
        nmat : dict of DataFrames
            The processed note matrix with internal Python lists.

        Returns
        -------
        export_nmat : dict of DataFrames
            A new dictionary where list-valued columns are stringified.
        """
        list_columns = [
            'f0Vals', 'pwrVals', 'specCentVals', 'specBandwidthVals',
            'specContrastVals', 'specFlatnessVals', 'specRolloffVals'
        ]
        
        export_nmat = {}
        for part, df in nmat.items():
            df_copy = df.copy()
            for col in list_columns:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col].apply(lambda x: str(x))
            export_nmat[part] = df_copy

        return export_nmat


    nmat_export = convert_nmat_for_export(nmat)

    if getattr(piece, 'fileExtension') != 'csv':                
        fileOutput = piece.insertAudioAnalysis(
            output_path=f"{output_path}.mei", data=nmat_export, mimetype='audio/aiff', target=audio_file_path)
        print(f"Saved: {output_path}.mei")
    else:
        # Save each part of nmat to a CSV file
        for part, df in nmat_export.items():
            # Construct the filename using the filepath, label, and part
            
            filename = f"{output_path}.csv"

            # Save the DataFrame to CSV
            fileOutput = df.to_csv(filename)
            print(f"Saved {filename}")    
    return nmat, fileOutput


def export_selected_columns(nmat, columns, output_path="./output_selected_data.csv"):
    """
        Export specified columns from a dictionary of DataFrames, a single DataFrame,
        or a NumPy array of DataFrames to a CSV. Missing columns are added as NaN.        

        Parameters
        ----------
        nmat : dict of DataFrames
            The dictionary of nmat with all relevant onset, offset, duration, and pitch information,
        columns : array of strings
            List of column names and order in which they are exported        
        output_path : str, optional
            The file path for the output CSV file. Defaults to './output_selected_data'.


        Returns
        -------
        plt : png file
            A PNG image of the spectrogram, overlay, and information
    """   
    save_dir = "./"
    os.makedirs(save_dir, exist_ok=True)
    selected = []

    if isinstance(nmat, dict):
        dfs = nmat.values()
    elif isinstance(nmat, pd.DataFrame):
        dfs = [nmat]
    elif isinstance(nmat, np.ndarray) and all(isinstance(x, pd.DataFrame) for x in nmat):
        dfs = list(nmat)
    else:
        raise TypeError(f"Unsupported type for nmat: {type(nmat)}")

    for df in dfs:
        df = df.copy()
        for col in columns:
            if col not in df.columns:
                df[col] = pd.NA
        selected.append(df[columns])

    if not selected:
        print("No data to export.")
        return

    combined = pd.concat(selected, ignore_index=True)
    combined.to_csv(output_path, index=False)
    print(f"Exported selected columns to: {output_path}")


# Internal utility function, no documentation
# Visualization component
def midi_to_freq(midi):
    return 440.0 * (2 ** ((midi - 69) / 12))

# Enharmonic flat conversion
enharmonic_map = {
    "A#": "Bb", "C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab"
}

# Internal utility function, no documentation
def midi_to_flat_note(midi):
    note = librosa.midi_to_note(midi, unicode=False)
    for sharp, flat in enharmonic_map.items():
        if sharp in note:
            return note.replace(sharp, flat)
    return note

# Change output_path to output_path like dataCompilation has
def visualise_alignment_from_nmat(nmat_dict, y, sr, output_path="output_visual"):
    """
        Creates a spectrogram with pitch, voice, and duration information overlaid.

        Parameters
        ----------
        nmat_dict : dict of DataFrames
            The dictionary of nmat with all relevant onset, offset, duration, and pitch information,
        y : ndarray
            Audio time series of the file.
        sr : int
            Original sample rate of the audio file.
        output_path : str, optional
            The file path for the output MEI file. Defaults to './output_visual'.


        Returns
        -------
        plt : png file
            A PNG image of the spectrogram, overlay, and information
    """    

    S = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    plt.figure(figsize=(12, 6))
    librosa.display.specshow(S, sr=sr, x_axis='time', y_axis='log', cmap='gray_r')
    plt.title(f"Spectrogram + Notes: {output_path}")

    # Generate consistent color palette
    base_colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
    color_cycle = (base_colors * ((len(nmat_dict) // len(base_colors)) + 1))[:len(nmat_dict)]

    part_name_map = {}
    legend_elements = []

    for idx, (original_name, notes) in enumerate(nmat_dict.items()):
        if notes.empty:
            continue

        new_name = f"Part-{idx + 1}"
        part_name_map[original_name] = new_name
        current_color = color_cycle[idx]
        legend_elements.append(Patch(facecolor=current_color, label=new_name))

        for _, row in notes.iterrows():
            if not all(k in row for k in ("MIDI", "ONSET_SEC", "OFFSET_SEC")):
                continue
            midi = row["MIDI"]
            start = row["ONSET_SEC"]
            end = row["OFFSET_SEC"]
            freq = midi_to_freq(midi)

            plt.fill_between([start, end], freq - 15, freq + 15, color=current_color, alpha=0.4)

            note_name = midi_to_flat_note(midi)
            plt.text((start + end) / 2, freq + 18, note_name,
                     ha='center', va='bottom', fontsize=8, color=current_color)

    plt.ylim(20, 2000)
    plt.colorbar(format='%+2.0f dB')
    plt.legend(handles=legend_elements, loc='upper right')

    save_path = os.path.join(f"{output_path}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")