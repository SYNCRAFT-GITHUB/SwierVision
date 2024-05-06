import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class KnownError(Gtk.Window):
    def __init__(self, error: str, message: str, code: str):
        self.error = error
        self.message = message
        self.code = code

known_errors = [
    KnownError(
        error= 'The Filament is not inserted into the first feeder',
        message= 'The Filament is not inserted into the first feeder',
        code=None
        ),
    KnownError(
        error= 'The Filament is not inserted into the second feeder',
        message= 'The Filament is not inserted into the second feeder',
        code=None
        ),
    KnownError(
        error= 'The inserted Extruder is incompatible with this File',
        message= 'The inserted Extruder is incompatible with this File',
        code=None
        ),
    KnownError(
        error= 'The material you\'re using is not compatible with this file',
        message= 'The material you\'re using is not compatible with this file',
        code=None
        ),
    KnownError(
        error= '!SOME_MATERIAL_DOESNT_MATCH_GCODE',
        message= 'One of the materials you\'re using is not compatible with this file',
        code=None
        ),
    KnownError(
        error= 'The file you are trying to print is for a different printer model',
        message= 'The file you are trying to print is for a different printer model',
        code=None
        ),
    KnownError(
        error= 'Both feeders must have materials inserted',
        message= 'Both feeders must have materials inserted',
        code=None
        ),
    KnownError(
        error= 'Nozzle height difference limit exceeded.',
        message= 'Incompatible height, mechanically calibrate to fix.',
        code=None
        ),
    KnownError(
        error= 'Probe triggered prior to movement',
        message= 'PROBE TRIGGERED PRIOR TO MOVEMENT',
        code=None
        ),
    KnownError(
        error= 'Already in a manual Z probe. Use ABORT to abort it.',
        message= 'ALREADY IN A MANUAL Z PROBE. USE ABORT TO ABORT IT',
        code=None
        ),
    KnownError(
        error= 'Endstop x still triggered after retract',
        message= 'ENDSTOP X STILL TRIGGERED AFTER RETRACT',
        code=None
        ),
    KnownError(
        error= 'No trigger on probe after full movement',
        message= 'NO TRIGGER ON PROBE AFTER FULL MOVEMENT',
        code=None
        ),
    KnownError(
        error= 'Probe samples exceed samples_tolerance',
        message= 'PROBE SAMPLES EXCEED SAMPLES_TOLERANCE',
        code=None
        ),
]