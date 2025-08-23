
from cmlibs.widgets.ui.ui_displaysettingswidget import Ui_DisplaySettings


def _display_settings_visibility(widget, setting_group):
    """
    Set the visibility of a widget based on the setting name.

    :param widget: The widget to modify.
    :param setting_group: The name of the group to set visibility for.
    """
    if setting_group == 'fieldfitter':
        widget.displayDataEmbedded_checkBox.setVisible(False)
        widget.displayDataGroup_frame.setVisible(False)
        widget.displayDataRadius_checkBox.setVisible(False)
        widget.displayDataMarkers_frame.setVisible(False)
        widget.displayDataProjectionTangents_checkBox.setVisible(False)
        widget.displayGroup_frame.setVisible(False)
        widget.displayDataLines_checkBox.setVisible(False)
        widget.displayMarker_frame.setVisible(False)
        widget.displayNodeDerivatives_checkBox.setVisible(False)
        widget.displayNodeDerivativeLabels_frame.setVisible(False)
        widget.displayNodeDerivativesVersion_spinBox.setVisible(False)
        widget.displayModelCoordinates_frame.setVisible(False)
        widget.displayMarkerPoints_checkBox.setVisible(False)
        widget.displayModelRadius_checkBox.setVisible(False)
        widget.displayTheme_frame.setVisible(False)
        widget.displayZeroJacobianContours_checkBox.setVisible(False)
    elif setting_group == 'scaffoldcreator':
        widget.displayDataEmbedded_checkBox.setVisible(False)
        widget.displayDataField_frame.setVisible(False)
        widget.displayDataProjections_checkBox.setVisible(False)
        widget.displayDataProjectionPoints_checkBox.setVisible(False)
        widget.displayDataProjectionTangents_checkBox.setVisible(False)
        widget.displayElementFieldPoints_checkBox.setVisible(False)
        widget.displayGroup_frame.setVisible(False)
        widget.displayTime_frame.setVisible(False)
        widget.displayField_frame.setVisible(False)
        widget.displayModelRadius_checkBox.setVisible(False)
    elif setting_group == 'geometryfitter':
        widget.displayDataEmbedded_checkBox.setVisible(False)
        widget.displayDataField_frame.setVisible(False)
        widget.displayDataGroup_frame.setVisible(False)
        widget.displayDataRadius_checkBox.setVisible(False)
        widget.displayTime_frame.setVisible(False)
        widget.displayField_frame.setVisible(False)
        widget.displayDataLines_checkBox.setVisible(False)
        widget.displayModelCoordinates_frame.setVisible(False)
        widget.displayElementFieldPoints_checkBox.setVisible(False)
        widget.displayNodeDerivativesVersion_spinBox.setVisible(False)
        widget.displayModelRadius_checkBox.setVisible(False)
        widget.displayTheme_frame.setVisible(False)
    elif setting_group == 'dataembedder':
        widget.displayDataField_frame.setVisible(False)
        widget.displayDataGroup_frame.setVisible(False)
        widget.displayDataRadius_checkBox.setVisible(False)
        widget.displayDataProjections_checkBox.setVisible(False)
        widget.displayDataProjectionPoints_checkBox.setVisible(False)
        widget.displayDataProjectionTangents_checkBox.setVisible(False)
        widget.displayDataMarkerProjections_checkBox.setVisible(False)
        widget.displayGroup_frame.setVisible(False)
        widget.displayNodeDerivatives_checkBox.setVisible(False)
        widget.displayNodeDerivativeLabels_frame.setVisible(False)
        widget.displayNodeDerivativesVersion_spinBox.setVisible(False)
        widget.displayModelRadius_checkBox.setVisible(False)
        widget.displayElementFieldPoints_checkBox.setVisible(False)
        widget.displayTheme_frame.setVisible(False)
        widget.displayZeroJacobianContours_checkBox.setVisible(False)
        widget.displayTime_frame.setVisible(False)
        widget.displayField_frame.setVisible(False)
    else:
        raise ValueError(f"Setting group '{setting_group}' is not recognized for display settings widget {widget.objectName()}.")


def setting_visibility(widget, setting_group):
    """
    Set the visibility of a widget based on the setting group name.

    :param widget: The widget to modify.
    :param setting_group: The name of the group to set visibility for.
    """
    if isinstance(widget, Ui_DisplaySettings):
        _display_settings_visibility(widget, setting_group)
    else:
        raise ValueError(f"Widget {type(widget)} is not recognized for setting visibility.")
