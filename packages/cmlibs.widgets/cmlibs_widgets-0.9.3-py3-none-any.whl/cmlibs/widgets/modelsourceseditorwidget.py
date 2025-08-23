"""
   Copyright 2015 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import os.path

from PySide6 import QtCore, QtGui, QtWidgets

from cmlibs.argon.argonmodelsources import ArgonModelSourceFile
from cmlibs.argon.argonlogger import ArgonLogger
from cmlibs.argon.argonerror import ArgonError
from cmlibs.argon.argonregion import REGION_PATH_SEPARATOR

from cmlibs.widgets.regionchooserwidget import RegionChooserWidget
from cmlibs.widgets.ui.ui_modelsourceseditorwidget import Ui_ModelSourcesEditorWidget

"""
Model Sources Editor Widget

Dialog for creation and editing list of model sources (files/resources)
read into a region in Qt / Python.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


class ModelSourcesModel(QtCore.QAbstractTableModel):

    def __init__(self, document, ex_files, parent=None, **kwargs):
        super(ModelSourcesModel, self).__init__(parent)
        self._headers = ['Value', 'Type', 'Region', 'Time', 'Add/Remove']
        self._document = document
        root_region = self._document.getRootRegion()
        root_region.connectRegionChange(self._applied_region_changed)

        source_names, self._document_model_sources = self._get_document_model_sources()

        for index, ex_file in enumerate(ex_files):
            if os.path.normpath(ex_file) not in source_names:
                self._add_file(ex_file)

        self._available_model_source_filenames = [m.getFileName() for m in self._document_model_sources]

        self._row_count = len(self._document_model_sources)
        self._update_common_path()

    def _add_file(self, file_name):
        model_source = ArgonModelSourceFile(file_name)
        model_source.setEdit(True)
        self._document.getRootRegion().addModelSource(model_source)
        self._document_model_sources.append(model_source)

    def _update_common_path(self):
        file_names = []
        for model_source in self._document_model_sources:
            file_names.append(os.path.normpath(model_source.getFileName()))

        try:
            if len(file_names) == 1:
                self._common_path = os.path.dirname(file_names[0])
            else:
                self._common_path = os.path.commonpath(file_names)

            self._common_path += os.path.sep
        except ValueError:
            self._common_path = ''

    def add_model_source_file(self, file_name):
        index = self.index(self._row_count, 0)
        self.beginInsertRows(index, self._row_count, self._row_count)
        self._add_file(file_name)
        self._available_model_source_filenames.append(file_name)
        self._row_count = len(self._document_model_sources)
        self._update_common_path()
        self.endInsertRows()

    def _get_document_child_model_sources(self, region):
        model_sources = []
        source_names = []
        region_model_sources = region.getModelSources()

        if region_model_sources:
            model_sources.extend(region_model_sources)
            source_names = [s.getFileName() for s in region_model_sources]

        for index in range(region.getChildCount()):
            child_source_names, child_model_sources = self._get_document_child_model_sources(region.getChild(index))
            source_names.extend(child_source_names)
            model_sources.extend(child_model_sources)

        return source_names, model_sources

    def _get_document_model_sources(self):
        return self._get_document_child_model_sources(self._document.getRootRegion())

    def _get_item_from_index(self, index):
        return self._document_model_sources[index.row()]

    def _get_region_path(self, item, region=None):
        if region is None:
            region = self._document.getRootRegion()

        model_sources = region.getModelSources()
        if item in model_sources:
            return region.getPath()
        else:
            for index in range(region.getChildCount()):
                child_region = region.getChild(index)
                result = self._get_region_path(item, child_region)
                if result is not None:
                    return result

        return None

    def rowCount(self, parent):
        return self._row_count

    def columnCount(self, parent):
        return 5

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self._get_item_from_index(index)

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return os.path.normpath(item.getFileName()).replace(self._common_path, '')
            elif index.column() == 1:
                return item.getType()
            elif index.column() == 2:
                return self._get_region_path(item)
            elif index.column() == 3:
                return item.getTime()
            elif index.column() == 4:
                return item.isLoaded()
        # elif role == QtCore.Qt.DecorationRole:
        #     if index.column() == 4:
        #         if item.isLoaded():
        #             return QtGui.QIcon(":/widgets/images/icons/list-remove-icon.png")
        #         return QtGui.QIcon(":/widgets/images/icons/list-add-icon.png")

        return None

    def _applied_region_changed(self, argon_region, modified):
        # A region may have been deleted, if it has add an editable model source to the root region.
        source_names, model_sources = self._get_document_model_sources()
        if len(source_names) != len(self._available_model_source_filenames):
            for index, file_name in enumerate(self._available_model_source_filenames):
                if os.path.normpath(file_name) not in source_names:
                    # Model source has been deleted, reset it to initial state.
                    model_source = self._document_model_sources[index]
                    model_source.setEdit(True)
                    model_source.unload()
                    self._document.getRootRegion().addModelSource(model_source)

        top_left_index = self.createIndex(0, 2)
        bottom_right_index = self.createIndex(self._row_count - 1, 2)
        self.dataChanged.emit(top_left_index, bottom_right_index)

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        if index.isValid():
            item = self._get_item_from_index(index)
            if role == QtCore.Qt.ItemDataRole.EditRole:
                top_left_index = index
                if index.column() == 2:
                    current_region = self._get_region_path(item)
                    if current_region != value:
                        region_old = self._document.findRegion(current_region)
                        region_old.removeModelSource(item)
                        region_new = self._document.findRegion(value)
                        region_new.addModelSource(item)
                elif index.column() == 3:
                    item.setTime(value)
                elif index.column() == 4:
                    region_index = self.createIndex(index.row(), 2)
                    region_path = self.data(region_index, QtCore.Qt.ItemDataRole.DisplayRole)
                    if value:
                        try:
                            region = self._document.findRegion(region_path)
                            region.applyModelSource(item)
                            # Set the region chooser cell as out-of-date for this model source item.
                            top_left_index = region_index
                        except ArgonError:
                            item.unload()
                            return False
                    # else:
                    #     region.removeModelSource(item)

                self.dataChanged.emit(top_left_index, index)
                return True

        return False

    def flags(self, index):
        if index.isValid():
            item = self._get_item_from_index(index)
            if index.column() == 0:
                return QtCore.Qt.ItemFlag.ItemIsEnabled
            elif index.column() in [2, 3]:
                if not item.isLoaded():
                    return QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled
            elif index.column() == 4:
                if item.isLoaded():
                    # Use the ItemIsUserTristate to indicate that the item is loaded and disabled.
                    return QtCore.Qt.ItemFlag.ItemIsUserTristate
                else:
                    return QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled

        return QtCore.Qt.ItemFlag.NoItemFlags

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._headers[section]


class RegionDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, root_region, parent=None):
        super(RegionDelegate, self).__init__(parent)
        self._root_region = root_region
        self._combo = None
        self._combo_boxes = []

    def createEditor(self, parent, option, index):
        len_existing = len(self._combo_boxes)
        if len_existing <= index.row():
            self._combo_boxes.extend([None] * (index.row() + 1 - len_existing))

        combo = RegionChooserWidget(parent)
        combo.setRootRegion(self._root_region)
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        self._combo_boxes[index.row()] = combo
        return combo

    def paint(self, painter, option, index):
        if isinstance(option.widget, QtWidgets.QAbstractItemView) and not option.widget.isPersistentEditorOpen(index):
            option.widget.openPersistentEditor(index)

        if len(self._combo_boxes) > index.row() and self._combo_boxes[index.row()] is not None:
            self._combo_boxes[index.row()].setEnabled(index.flags() != QtCore.Qt.ItemFlag.NoItemFlags)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.ItemDataRole.DisplayRole)

        if len(value) > 1 and value.endswith(REGION_PATH_SEPARATOR):
            value = value[:-1]

        editor.blockSignals(True)
        editor.setCurrentText(value)
        editor.blockSignals(False)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


class ApplyDelegate(QtWidgets.QItemDelegate):
    """
    A delegate that acts like a checkbox to the cell of the column to which
    it's applied.
    """

    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self._add_icon = QtGui.QIcon(":/widgets/images/icons/list-add-icon.png")
        self._add_disabled_icon = QtGui.QIcon(":/widgets/images/icons/list-add-disabled-icon.png")
        self._remove_icon = QtGui.QIcon(":/widgets/images/icons/list-remove-icon.png")
        self._remove_disabled_icon = QtGui.QIcon(":/widgets/images/icons/list-remove-disabled-icon.png")

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        if index.flags() == QtCore.Qt.ItemFlag.NoItemFlags:
            self._add_disabled_icon.paint(painter, option.rect)
        elif index.flags() == QtCore.Qt.ItemFlag.ItemIsUserTristate:
            self._remove_disabled_icon.paint(painter, option.rect)
        elif index.data():
            self._remove_icon.paint(painter, option.rect)
        else:
            self._add_icon.paint(painter, option.rect)

    def editorEvent(self, event, model, option, index):
        """
        Change the data in the model and the state of the checkbox
        if the user presses the left mouse button and this cell is editable. Otherwise
        do nothing.
        """
        if not index.flags() & QtCore.Qt.ItemFlag.ItemIsEditable:
            return False

        if event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Change the checkbox-state
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData(self, editor, model, index):
        """
        Toggle the data state.
        """
        model.setData(index, not index.data(), QtCore.Qt.ItemDataRole.EditRole)


class ModelSourcesEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._region = None
        self._currentModelSource = None
        self._itemModel = None
        self._enable_old_model_sources = False
        self._enable_adding_model_sources = True
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_ModelSourcesEditorWidget()
        self._ui.setupUi(self)

        self._update_ui()
        self._makeConnections()

    def _makeConnections(self):
        self._ui.listViewModelSources.clicked.connect(self._listSourceItemClicked)
        self._ui.comboBoxAddSource.currentIndexChanged.connect(self._addSourceEntered)
        self._ui.pushButtonApplySource.clicked.connect(self._applySourceClicked)
        self._ui.pushButtonDeleteSource.clicked.connect(self._deleteSourceClicked)
        self._ui.pushButtonBrowseFileName.clicked.connect(self._fileBrowseClicked)
        self._ui.lineEditTime.editingFinished.connect(self._fileTimeEntered)
        self._ui.pushButtonAddSource.clicked.connect(self._addSourceClicked)

    def setEnableAddingModelSources(self, state=True):
        self._enable_adding_model_sources = state
        self._update_ui()

    def setModelSourcesModel(self, root_region, model):
        self._ui.tableViewModelSources.setModel(model)
        self._ui.tableViewModelSources.setItemDelegateForColumn(2, RegionDelegate(root_region, self._ui.tableViewModelSources))
        self._ui.tableViewModelSources.setItemDelegateForColumn(4, ApplyDelegate(self._ui.tableViewModelSources))

    def getRegion(self):
        return self._region

    def setRegion(self, region):
        """
        :param region: ArgonRegion to edit model sources for
        """
        self._region = region
        self._buildSourcesList()

    def _update_ui(self):
        self._ui.groupBoxAddSource.setVisible(self._enable_old_model_sources)
        self._ui.frameOldModelSources.setVisible(self._enable_old_model_sources)
        self._ui.listViewModelSources.setVisible(self._enable_old_model_sources)
        self._ui.pushButtonAddSource.setVisible(self._enable_adding_model_sources)
        # self._ui.pushButtonDeleteSource.setVisible(self._enable_adding_model_sources)
        # self._ui.comboBoxAddSource.setVisible(self._enable_adding_model_sources)

    def _buildSourcesList(self):
        """
        Fill the list view with the list of model sources for current region
        """
        # This function should no longer be used, delete in the next version.
        self._itemModel = QtGui.QStandardItemModel(self._ui.listViewModelSources)
        currentIndex = None
        modelSources = []
        if self._region:
            modelSources = self._region.getModelSources()
            # selectedGraphics = self.view.graphics_editor.getGraphics()
            for modelSource in modelSources:
                name = modelSource.getDisplayName()
                item = QtGui.QStandardItem(name)
                item.setData(modelSource)
                item.setEditable(False)
                self._itemModel.appendRow(item)
                if modelSource == self._currentModelSource:
                    currentIndex = self._itemModel.indexFromItem(item)
        self._ui.listViewModelSources.setModel(self._itemModel)
        if currentIndex is None:
            if len(modelSources) > 0:
                modelSource = modelSources[0]
                currentIndex = self._itemModel.createIndex(0, 0)  # , self._itemModel.item(0))
            else:
                modelSource = None
            self._setCurrentModelSource(modelSource)
        if currentIndex is not None:
            self._ui.listViewModelSources.setCurrentIndex(currentIndex)
        self._ui.listViewModelSources.show()

    def _refreshCurrentItem(self):
        if self._currentModelSource:
            name = self._currentModelSource.getDisplayName()
            currentIndex = self._ui.listViewModelSources.currentIndex()
            item = self._itemModel.item(currentIndex.row())
            item.setText(name)

    def _listSourceItemClicked(self, modelIndex):
        """
        Item in list of model sources selected
        """
        model = modelIndex.model()
        item = model.item(modelIndex.row())
        modelSource = item.data()
        self._setCurrentModelSource(modelSource)

    def _addSourceEntered(self, index):
        """
        Add a new model source with type given in name
        """
        if not self._region:
            return
        name = self._ui.comboBoxAddSource.currentText()
        modelSource = None
        if name == "File":
            modelSource = ArgonModelSourceFile(file_name="")
            modelSource.setEdit(True)
        if modelSource:
            self._region.addModelSource(modelSource)
            self._setCurrentModelSource(modelSource)
            self._buildSourcesList()
        self._ui.comboBoxAddSource.setCurrentIndex(0)  # reset combo box we're using as a menu

    def _addSourceClicked(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Model Source", "", "Model Files (*.ex* *.fieldml)")
        if not fileName:
            return

        self._ui.tableViewModelSources.model().add_model_source_file(fileName)

    def _applySourceClicked(self):
        if self._region and self._currentModelSource:
            rebuildRegion = self._region.applyModelSource(self._currentModelSource)
            self._ui.pushButtonApplySource.setEnabled(self._currentModelSource.isEdit())
            self._refreshCurrentItem()

    def _deleteSourceClicked(self):
        if self._region and self._currentModelSource:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("Please confirm")
            msgBox.setText("Delete model data source?")
            # msgBox.setInformativeText("Please confirm action.")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Cancel)
            result = msgBox.exec_()
            if result == QtWidgets.QMessageBox.StandardButton.Ok:
                self._region.removeModelSource(self._currentModelSource)

    def _setCurrentModelSource(self, modelSource):
        if modelSource is not self._currentModelSource:
            self._currentModelSource = modelSource
            isFileType = False
            if modelSource:
                self._ui.pushButtonApplySource.setEnabled(modelSource.isEdit())
                isFileType = modelSource.getType() == "FILE"
                if isFileType:
                    self._fileNameDisplay()
                    self._fileTimeDisplay()
            self._ui.groupBoxAddSource.setVisible(isFileType)
        elif not modelSource:
            self._ui.groupBoxAddSource.setVisible(False)

    def _editedCurrentModelSource(self):
        if self._currentModelSource:
            self._currentModelSource.setEdit(True)
            self._refreshCurrentItem()
            self._ui.pushButtonApplySource.setEnabled(True)

    def _fileNameDisplay(self):
        if self._currentModelSource:
            fileName = self._currentModelSource.getFileName()
            self._ui.lineEditFileName.setText(fileName)

    def _fileBrowseClicked(self):
        fileNameTuple = QtWidgets.QFileDialog.getOpenFileName(self, "Select Model Source", "", "Model Files (*.ex* *.fieldml)")
        fileName = fileNameTuple[0]
        # fileFilter = fileNameTuple[1]
        if not fileName:
            return
        self._currentModelSource.setFileName(fileName)
        self._editedCurrentModelSource()
        # set current directory to path from file, to support scripts and fieldml with external resources
        self._fileNameDisplay()

    def _fileTimeDisplay(self):
        if self._currentModelSource:
            time = self._currentModelSource.getTime()
            text = "{:.5g}".format(time) if time is not None else ""
            self._ui.lineEditTime.setText(text)

    def _fileTimeEntered(self):
        timeText = self._ui.lineEditTime.text().strip()
        try:
            if timeText == "":
                time = None
            else:
                time = float(timeText)
            self._currentModelSource.setTime(time)
            self._editedCurrentModelSource()
        except:
            ArgonLogger.getLogger().error("Invalid time", timeText)
        self._fileTimeDisplay()
