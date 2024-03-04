import numpy as np
from scipy import signal as sp

def add_awgn(iqdata: np.ndarray, snr_db: float) -> np.ndarray:
    """Add AWGN noise to a given real valued 2D iq sample array.

    Args:
        iqdata (np.ndarray): The iq array to add noise to.
        snr_db (float): The desired SNR level.

    Returns:
        noise_iqdata: The iq array with added noise.
    """

    # Calculate the noise power based on SNR (in dB)
    snr_linear = 10 ** (snr_db / 10)  # Convert dB to linear scale
    signal_power = np.mean(np.linalg.norm(iqdata, axis=0) ** 2)
    noise_power = signal_power / snr_linear

    # Generate Gaussian noise samples with the calculated noise power
    noise = np.sqrt(noise_power/2) * np.random.randn(*iqdata.shape)

    # Add noise to the signal
    noisy_iqdata = iqdata + noise

    return noisy_iqdata

def time_shift(iqdata: np.ndarray, t_shift: int) -> np.ndarray:
    """Adds a positive or negative time shift impairment in samples to a given 
    real valued 2D iq sample array. Empty regions either side are filled with 
    zeros.

    Args:
        iqdata (np.ndarray): The iq array to time shift.
        t_shift (int): The desired number of samples to shift by.

    Returns:
        shifted_iqdata: The iq array shifted in time.
    """

    shifted_iqdata = np.zeros_like(iqdata)

    # New iq array shifted left or right depending on sign of shift
    # This should work even if shift > iqdata.shape[1]
    if t_shift >= 0:
        shifted_iqdata[:,t_shift:] = iqdata[:,:-t_shift]
    else:
        shifted_iqdata[:,:t_shift] = iqdata[:,-t_shift:]

    return shifted_iqdata

def frequency_shift(iqdata: np.ndarray, f_shift: float) -> np.ndarray:
    """Shifts the frequency of a 2D iq sample array relative to the sample rate.
    
    Args:
        iqdata (np.ndarray): The iq array to frequency shift.
        f_shift (float): The frequency shift relative to the sample rate in the 
            range [-.5, .5].

    Returns:
        shifted_iqdata: The frequency shifted iq samples.
    """

    shifted_iqdata = np.zeros_like(iqdata)

    # Calculate the phase shift for the frequency shift
    phase_shift = 2.0 * np.pi * f_shift * np.arange(iqdata.shape[1])

    # Use trigonometric identities to apply the frequency shift
    shifted_iqdata[0] = iqdata[0] * np.cos(phase_shift) - iqdata[1] * \
        np.sin(phase_shift)
    shifted_iqdata[1] = iqdata[0] * np.sin(phase_shift) + iqdata[1] * \
        np.cos(phase_shift)

    return shifted_iqdata

def phase_shift(iqdata: np.ndarray, phase: float) -> np.ndarray:
    """Applies a phase shift to a 2D iq sample array by phase rotation.
    
    Args:
        iqdata (np.ndarray): The iq array to phase shift.
        phase (float): The phase to rotate the iq sample array by in the range 
            [-pi, pi].

    Returns:
        shifted_iqdata: The phase shifted iq samples.
    """

    iqdata = iqdata[0] + 1j * iqdata[1]
    iqdata * np.exp(1j * phase)

    return np.array([iqdata.real, iqdata.imag])

def iq_imbalance(iqdata, amplitude_imbalance_db, 
                 phase_imbalance_rad, dc_offset_db) -> np.ndarray:
    """Applies IQ Imbalance to a 2D iq sample array. Implementation based off 
    of https://www.mathworks.com/help/comm/ref/iqimbalance.html

    Args:
        amplitude_imbalance_dB (float): IQ amplitude imbalance in dB.
        
        phase_imbalance_rad (float): IQ phase imbalance in radians [-pi, pi].

        dc_offset_db (float): IQ DC offset in dB.

    Returns:
        imbalanced_iqdata: The IQ sample array with applied IQ imbalance.
    """

    iqdata = iqdata[0] + 1j * iqdata[1]

    # Apply amplitude imbalance
    iqdata = 10 ** (0.5*amplitude_imbalance_db / 20.0) * iqdata.real + \
        1j * 10 ** (-0.5*amplitude_imbalance_db / 20.0) * iqdata.imag

    # Apply phase imbalance
    iqdata = np.exp(-1j * phase_imbalance_rad / 2.0) * iqdata.real + \
             np.exp(1j * (np.pi / 2.0  + phase_imbalance_rad / 2.0)) * \
                iqdata.imag
    
    # Apply DC offset
    iqdata += 10 ** (dc_offset_db / 20.0) * iqdata.real + \
         1j * 10 ** (dc_offset_db / 20.0) * iqdata.imag
    
    return np.array([iqdata.real, iqdata.imag])

def resample(iqdata: np.ndarray, up: int, down: int) -> np.ndarray:
    """Resamples a 2D iq sample array based on the provided up and downsampling
    rates. The resulting sample rate is up / down times the original sample 
    rate.
    See https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html
    
    Args:
        iqdata (np.ndarray): The iq array to resample.
        up: The upsampling factor.
        down: The downsampling factor.

    Returns:
        resampled_iqdata: The resampled array.
    """

    iqdata_shape = iqdata.shape

    resampled_iqdata = sp.resample_poly(iqdata, up, down)
    if resampled_iqdata.shape[1] > iqdata_shape[1]:
        resampled_iqdata = resampled_iqdata[:,:iqdata_shape[1]]
    else:
        empty_array = np.zeros(iqdata_shape)
        empty_array[:,:resampled_iqdata.shape[1]] = resampled_iqdata

    return resampled_iqdata