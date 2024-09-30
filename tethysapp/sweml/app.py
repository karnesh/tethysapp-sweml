from tethys_sdk.base import TethysAppBase


class Sweml(TethysAppBase):
    """
    Tethys app class for SWEML.
    """

    name = 'SWEML'
    description = 'App to display 1-km resolution SWE prediction from deep learning models'
    package = 'sweml'  # WARNING: Do not change this value
    index = 'swe'
    icon = f'{package}/images/Superior.jpg'
    root_url = 'sweml'
    color = '#c23616'
    tags = '"SWE", "Deep learning", "1-km resolution"'
    enable_feedback = False
    feedback_emails = []