"""CTypes signatures for every function & enum exposed in ``aic_c.h``.

This module provides a thin, typed layer over the C API exposed by the SDK.
Most users should prefer the higher-level :pyclass:`aic.Model` wrapper.
"""

from __future__ import annotations

import ctypes as _ct
from enum import IntEnum
from typing import Any

from ._loader import load

################################################################################
#  Automatically extracted enums – edit in aic/_generate_bindings.py instead  #
################################################################################


class AICErrorCode(IntEnum):
    """Error codes returned by the C API.

    These mirror the values from the underlying SDK and are raised as
    ``RuntimeError`` by the thin wrappers in this module when a call
    does not succeed.
    """

    SUCCESS = 0
    """Operation completed successfully."""

    NULL_POINTER = 1
    """Required pointer argument was NULL."""

    LICENSE_INVALID = 2
    """License key format is invalid or corrupted."""

    LICENSE_EXPIRED = 3
    """License key has expired."""

    UNSUPPORTED_AUDIO_CONFIG = 4
    """Audio configuration is not supported by the model."""

    AUDIO_CONFIG_MISMATCH = 5
    """Process was called with a different audio buffer configuration than initialized."""

    NOT_INITIALIZED = 6
    """Model must be initialized before this operation."""

    PARAMETER_OUT_OF_RANGE = 7
    """Parameter value is outside acceptable range."""

    SDK_ACTIVATION_ERROR = 8
    """SDK activation failed."""


class AICModelType(IntEnum):
    """Available model types for audio enhancement.

    Each model is optimized for a native sample rate and frame size and has
    a characteristic processing latency.
    """

    # Detailed variants with native rates and frame sizes
    QUAIL_L48 = 0
    """Specifications:

    - Native sample rate: 48 kHz
    - Native num frames: 480
    - Processing latency: 30 ms
    """
    QUAIL_L16 = 1
    """Specifications:

    - Native sample rate: 16 kHz
    - Native num frames: 160
    - Processing latency: 30 ms
    """
    QUAIL_L8 = 2
    """Specifications:

    - Native sample rate: 8 kHz
    - Native num frames: 80
    - Processing latency: 30 ms
    """
    QUAIL_S48 = 3
    """Specifications:

    - Native sample rate: 48 kHz
    - Native num frames: 480
    - Processing latency: 30 ms
    """
    QUAIL_S16 = 4
    """Specifications:

    - Native sample rate: 16 kHz
    - Native num frames: 160
    - Processing latency: 30 ms
    """
    QUAIL_S8 = 5
    """Specifications:

    - Native sample rate: 8 kHz
    - Native num frames: 80
    - Processing latency: 30 ms
    """
    QUAIL_XS = 6
    """Specifications:

    - Native sample rate: 48 kHz
    - Native num frames: 480
    - Processing latency: 10 ms
    """
    QUAIL_XXS = 7
    """Specifications:

    - Native sample rate: 48 kHz
    - Native num frames: 480
    - Processing latency: 10 ms
    """

    # Backwards-compatible aliases
    QUAIL_L = 0
    QUAIL_S = 3


class AICParameter(IntEnum):
    """Configurable parameters for audio enhancement."""

    ENHANCEMENT_LEVEL = 0
    """Controls the intensity of speech enhancement processing.

    Range: 0.0 … 1.0

    - 0.0: Bypass (original signal passes through unchanged)
    - 1.0: Full enhancement (maximum noise reduction, potentially more artifacts)

    Default: 1.0
    """

    VOICE_GAIN = 1
    """Compensates for perceived volume reduction after noise removal.

    Range: 0.1 … 4.0 (linear amplitude multiplier)

    - 0.1: Significant volume reduction (≈ −20 dB)
    - 1.0: No gain change (0 dB, default)
    - 2.0: Double amplitude (+6 dB)
    - 4.0: Maximum boost (+12 dB)

    Formula: gain_dB = 20 × log10(value)
    Default: 1.0
    """

    NOISE_GATE_ENABLE = 2
    """Enable or disable a noise gate as a pre-processing step.

    Valid values: 0.0 or 1.0

    - 0.0: Noise gate disabled (C library default)
    - 1.0: Noise gate enabled

    Default: 0.0
    """


################################################################################
#                       struct forward declarations                             #
################################################################################


class _AICModel(_ct.Structure):
    pass


AICModelPtr = _ct.POINTER(_AICModel)
# Alias for annotations to satisfy static type checkers (no TypeAlias to support py3.9)
AICModelPtrT = Any

################################################################################
#                       function prototypes                                     #
################################################################################

_LIB: _ct.CDLL | None = None
_PROTOTYPES_CONFIGURED = False


def _get_lib() -> _ct.CDLL:
    """Return the loaded C library, loading and configuring prototypes lazily."""
    global _LIB, _PROTOTYPES_CONFIGURED
    if _LIB is None:
        _LIB = load()
    if not _PROTOTYPES_CONFIGURED:
        lib = _LIB
        # function prototypes
        lib.aic_model_create.restype = AICErrorCode
        lib.aic_model_create.argtypes = [
            _ct.POINTER(AICModelPtr),  # **model
            _ct.c_int,  # model_type (AICModelType)
            _ct.c_char_p,  # license_key
        ]

        lib.aic_model_destroy.restype = None
        lib.aic_model_destroy.argtypes = [AICModelPtr]

        lib.aic_model_initialize.restype = AICErrorCode
        lib.aic_model_initialize.argtypes = [
            AICModelPtr,
            _ct.c_uint32,  # sample_rate
            _ct.c_uint16,  # num_channels
            _ct.c_size_t,  # num_frames
        ]

        lib.aic_model_reset.restype = AICErrorCode
        lib.aic_model_reset.argtypes = [AICModelPtr]

        lib.aic_model_process_planar.restype = AICErrorCode
        lib.aic_model_process_planar.argtypes = [
            AICModelPtr,
            _ct.POINTER(_ct.POINTER(_ct.c_float)),  # float* const* audio
            _ct.c_uint16,  # num_channels
            _ct.c_size_t,  # num_frames
        ]

        lib.aic_model_process_interleaved.restype = AICErrorCode
        lib.aic_model_process_interleaved.argtypes = [
            AICModelPtr,
            _ct.POINTER(_ct.c_float),  # float* audio
            _ct.c_uint16,
            _ct.c_size_t,
        ]

        lib.aic_model_set_parameter.restype = AICErrorCode
        lib.aic_model_set_parameter.argtypes = [
            AICModelPtr,
            _ct.c_int,  # parameter (AICParameter)
            _ct.c_float,
        ]

        lib.aic_model_get_parameter.restype = AICErrorCode
        lib.aic_model_get_parameter.argtypes = [
            AICModelPtr,
            _ct.c_int,  # parameter (AICParameter)
            _ct.POINTER(_ct.c_float),
        ]

        # delay API (new in >=0.6.0, fallback to old symbol when running older libs)
        if hasattr(lib, "aic_get_output_delay"):
            lib.aic_get_output_delay.restype = AICErrorCode
            lib.aic_get_output_delay.argtypes = [
                AICModelPtr,
                _ct.POINTER(_ct.c_size_t),
            ]
        else:
            lib.aic_get_processing_latency = lib.aic_get_processing_latency  # type: ignore[attr-defined]
            lib.aic_get_processing_latency.restype = AICErrorCode
            lib.aic_get_processing_latency.argtypes = [
                AICModelPtr,
                _ct.POINTER(_ct.c_size_t),
            ]

        lib.aic_get_optimal_sample_rate.restype = AICErrorCode
        lib.aic_get_optimal_sample_rate.argtypes = [
            AICModelPtr,
            _ct.POINTER(_ct.c_uint32),
        ]

        lib.aic_get_optimal_num_frames.restype = AICErrorCode
        lib.aic_get_optimal_num_frames.argtypes = [
            AICModelPtr,
            _ct.POINTER(_ct.c_size_t),
        ]

        # version API (new in >=0.6.0, fallback to old symbol when running older libs)
        if hasattr(lib, "aic_get_sdk_version"):
            lib.aic_get_sdk_version.restype = _ct.c_char_p
            lib.aic_get_sdk_version.argtypes = []
        else:
            lib.get_library_version.restype = _ct.c_char_p
            lib.get_library_version.argtypes = []
        _PROTOTYPES_CONFIGURED = True
    return _LIB


################################################################################
#                     thin pythonic convenience wrappers                        #
################################################################################


def model_create(model_type: AICModelType, license_key: bytes) -> AICModelPtrT:
    """Create a new audio enhancement model instance.

    Multiple models can be created to process different audio streams
    simultaneously or to switch between enhancement algorithms.

    Parameters
    ----------
    model_type : AICModelType
        Selects the enhancement algorithm variant.
    license_key : bytes
        Null-terminated license string. Must not be empty.

    Returns
    -------
    AICModelPtrT
        Opaque handle to the created model instance.

    Raises
    ------
    RuntimeError
        If the underlying C call fails. The error message includes
        the corresponding :class:`AICErrorCode` name from the SDK.

    """
    lib = _get_lib()
    mdl = AICModelPtr()
    err = lib.aic_model_create(_ct.byref(mdl), model_type, license_key)
    _raise(err)
    return mdl


def model_destroy(model: AICModelPtrT) -> None:
    """Release all resources associated with a model instance.

    Safe to call with a null/invalid handle; the operation is idempotent.

    Parameters
    ----------
    model : AICModelPtrT
        Model instance to destroy. Can be ``None``.

    Returns
    -------
    None

    """
    lib = _get_lib()
    lib.aic_model_destroy(model)


def model_initialize(model: AICModelPtrT, sample_rate: int, num_channels: int, num_frames: int) -> None:
    """Configure the model for a specific audio format.

    Must be called before processing. For the lowest delay use the values
    returned by :func:`get_optimal_sample_rate` and
    :func:`get_optimal_num_frames`.

    Parameters
    ----------
    model : AICModelPtrT
        Model handle. Must not be ``None``.
    sample_rate : int
        Audio sample rate in Hz (8000–192000).
    num_channels : int
        Number of audio channels (1 for mono, 2 for stereo, etc.).
    num_frames : int
        Number of samples per channel per processing call.

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
        If the configuration is not supported by the model.

    Notes
    -----
    Not real-time safe: do not call from time-critical audio threads.

    """
    lib = _get_lib()
    _raise(lib.aic_model_initialize(model, sample_rate, num_channels, num_frames))


def model_reset(model: AICModelPtrT) -> None:
    """Clear all internal state and buffers (real-time safe).

    Call this when the audio stream is interrupted or when seeking to
    prevent artifacts from previous audio content. The model remains
    initialized with the same configuration.

    Parameters
    ----------
    model : AICModelPtrT
        Model instance. Must not be ``None``.

    Returns
    -------
    None

    """
    lib = _get_lib()
    _raise(lib.aic_model_reset(model))


def process_planar(model: AICModelPtrT, audio_ptr: Any, num_channels: int, num_frames: int) -> None:
    """Process audio in-place with separate buffers per channel (planar layout).

    Parameters
    ----------
    model : AICModelPtrT
        Initialized model instance.
    audio_ptr : Any
        Array of channel buffer pointers (``float* const*`` on the C side).
    num_channels : int
        Number of channels (must match initialization; max 16 channels).
    num_frames : int
        Number of samples per channel (must match initialization).

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
        If the model is not initialized, inputs are null, or the channel/frame
        configuration does not match the initialization.

    """
    lib = _get_lib()
    _raise(lib.aic_model_process_planar(model, audio_ptr, num_channels, num_frames))


def process_interleaved(model: AICModelPtrT, audio_ptr: Any, num_channels: int, num_frames: int) -> None:
    """Process audio in-place with interleaved channel data.

    Parameters
    ----------
    model : AICModelPtrT
        Initialized model instance.
    audio_ptr : Any
        Interleaved audio buffer pointer.
    num_channels : int
        Number of channels (must match initialization).
    num_frames : int
        Number of frames per channel (must match initialization).

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
        If the model is not initialized, inputs are null, or the channel/frame
        configuration does not match the initialization.

    """
    lib = _get_lib()
    _raise(lib.aic_model_process_interleaved(model, audio_ptr, num_channels, num_frames))


def set_parameter(model: AICModelPtrT, param: AICParameter, value: float) -> None:
    """Modify a model parameter (thread-safe).

    Parameters
    ----------
    model : AICModelPtrT
        Model instance. Must not be ``None``.
    param : AICParameter
        Parameter to modify.
    value : float
        New parameter value. See parameter docs for valid ranges.

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
        If the value is outside the acceptable range.

    """
    lib = _get_lib()
    _raise(lib.aic_model_set_parameter(model, param, value))


def get_parameter(model: AICModelPtrT, param: AICParameter) -> float:
    """Retrieve the current value of a parameter (thread-safe).

    Parameters
    ----------
    model : AICModelPtrT
        Model instance. Must not be ``None``.
    param : AICParameter
        Parameter to query.

    Returns
    -------
    float
        The current value of the parameter.

    """
    lib = _get_lib()
    out = _ct.c_float()
    _raise(lib.aic_model_get_parameter(model, param, _ct.byref(out)))
    return float(out.value)


def get_processing_latency(model: AICModelPtrT) -> int:
    """Return total output delay in samples for the current configuration.

    Delay behavior
    --------------
    - Before initialization: returns the base processing delay using the
      model's optimal frame size at its native sample rate.
    - After initialization: returns the actual delay for the configured
      sample rate and frame size, including any additional buffering when
      using non-optimal frame sizes.

    Parameters
    ----------
    model : AICModelPtrT
        Model instance. Must not be ``None``.

    Returns
    -------
    int
        Delay in samples (at the current sample rate). Convert to milliseconds
        via ``delay_ms = delay_samples * 1000 / sample_rate``.

    """
    lib = _get_lib()
    out = _ct.c_size_t()
    if hasattr(lib, "aic_get_output_delay"):
        _raise(lib.aic_get_output_delay(model, _ct.byref(out)))  # type: ignore[attr-defined]
    else:
        _raise(lib.aic_get_processing_latency(model, _ct.byref(out)))  # type: ignore[attr-defined]
    return int(out.value)


def get_output_delay(model: AICModelPtrT) -> int:
    """Alias of :func:`get_processing_latency`.

    Parameters
    ----------
    model : AICModelPtrT
        Model instance.

    Returns
    -------
    int
        Delay in samples.

    """
    return get_processing_latency(model)


def get_optimal_sample_rate(model: AICModelPtrT) -> int:
    """Return the model's native sample rate in Hz.

    Each model is optimized for a specific sample rate. While processing at
    other rates is supported, enhancement quality for high frequencies is
    bounded by the model's native Nyquist frequency.

    Parameters
    ----------
    model : AICModelPtrT
        Model instance.

    Returns
    -------
    int
        Native/optimal sample rate in Hz.

    """
    lib = _get_lib()
    out = _ct.c_uint32()
    _raise(lib.aic_get_optimal_sample_rate(model, _ct.byref(out)))
    return int(out.value)


def get_optimal_num_frames(model: AICModelPtrT) -> int:
    """Return the optimal number of frames for minimal latency.

    Using the optimal frame size avoids internal buffering and thus minimizes
    end-to-end delay. The optimal value depends on sample rate and updates
    when the model is initialized with a different rate. Before initialization
    this returns the optimal size for the model's native sample rate.

    Parameters
    ----------
    model : AICModelPtrT
        Model instance.

    Returns
    -------
    int
        Optimal frame count for the current/native sample rate.

    """
    lib = _get_lib()
    out = _ct.c_size_t()
    _raise(lib.aic_get_optimal_num_frames(model, _ct.byref(out)))
    return int(out.value)


def get_library_version() -> str:
    """Return the SDK version string.

    The returned value originates from a static C string and is safe to use
    for the lifetime of the program.

    Returns
    -------
    str
        Semantic version string, for example ``"1.2.3"``.

    """
    lib = _get_lib()
    if hasattr(lib, "aic_get_sdk_version"):
        version_ptr = lib.aic_get_sdk_version()  # type: ignore[attr-defined]
    else:
        version_ptr = lib.get_library_version()  # type: ignore[attr-defined]
    return version_ptr.decode("utf-8")


# ------------------------------------------------------------------#
def _raise(err: AICErrorCode) -> None:
    if err != AICErrorCode.SUCCESS:
        raise RuntimeError(f"AIC-SDK error: {err.name}")
