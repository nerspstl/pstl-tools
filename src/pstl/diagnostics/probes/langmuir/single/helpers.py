from .classes import SingleProbeLangmuir, SphericalSingleProbeLangmuir, CylindericalSingleProbeLangmuir, PlanarSingleProbeLangmuir
from .classes import available_probe_classes
from pstl.utls.verify import verify_type

available_plasma_properties = [
    "V_f",
    "V_s",
    "KT_e",
    "lambda_De",
    "n_e",
    "n_i",
    "I_es",
    "I_is",
    "J_es",
    "J_is",
    "r_p/lambda_De",
    "sheath",
]


def shape_selector(shape:str):

    verify_type(shape,str)

    shape = shape.lower()
    if shape in available_probe_classes[0]:  # cylinderical
        probe = CylindericalSingleProbeLangmuir