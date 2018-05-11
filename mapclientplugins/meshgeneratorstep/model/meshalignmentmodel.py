
import json

from opencmiss.utils.maths import vectorops


class MeshAlignmentModel(object):

    def __init__(self):
        self._clear()

    def setScene(self, scene):
        self._scene = scene

    def isStateAlign(self):
        return self._isStateAlign

    def setStateAlign(self):
        self._isStateAlign = True

    def setAlignSettingsChangeCallback(self, alignSettingsChangeCallback):
        self._alignSettingsChangeCallback = alignSettingsChangeCallback

    def scaleModel(self, factor):
        self._alignSettings['scale'] *= factor
        self._applyAlignSettings()

    def rotateModel(self, axis, angle):
        quat = vectorops.axisAngleToQuaternion(axis, angle)
        mat1 = vectorops.rotmx(quat)
        mat2 = vectorops.eulerToRotationMatrix3(self._alignSettings['euler_angles'])
        newmat = vectorops.mxmult(mat1, mat2)
        self._alignSettings['euler_angles'] = vectorops.rotationMatrix3ToEuler(newmat)
        self._applyAlignSettings()

    def offsetModel(self, relativeOffset):
        self._alignSettings['offset'] = vectorops.add(self._alignSettings['offset'], relativeOffset)
        self._applyAlignSettings()

    def getAlignEulerAngles(self):
        return self._alignSettings['euler_angles']

    def setAlignEulerAngles(self, eulerAngles):
        if len(eulerAngles) == 3:
            self._alignSettings['euler_angles'] = eulerAngles
            self._applyAlignSettings()

    def getAlignOffset(self):
        return self._alignSettings['offset']

    def setAlignOffset(self, offset):
        if len(offset) == 3:
            self._alignSettings['offset'] = offset
            self._applyAlignSettings()

    def getAlignScale(self):
        return self._alignSettings['scale']

    def setAlignScale(self, scale):
        self._alignSettings['scale'] = scale
        self._applyAlignSettings()

    def resetAlignment(self):
        self._resetAlignSettings()
        self._applyAlignSettings()

    def loadAlignSettings(self):
        with open(self._location + '-align-settings.json', 'r') as f:
            self._alignSettings.update(json.loads(f.read()))
        self._applyAlignSettings()

    def saveAlignSettings(self):
        with open(self._location + '-align-settings.json', 'w') as f:
            f.write(json.dumps(self._alignSettings, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    def _resetAlignSettings(self):
        self._alignSettings = dict(euler_angles=[0.0, 0.0, 0.0], scale=1.0, offset=[0.0, 0.0, 0.0])

    def _applyAlignSettings(self):
        rot = vectorops.eulerToRotationMatrix3(self._alignSettings['euler_angles'])
        scale = self._alignSettings['scale']
        xScale = scale
        # if self.isAlignMirror():
        #     xScale = -scale
        rotationScale = [
            rot[0][0]*xScale, rot[0][1]*xScale, rot[0][2]*xScale,
            rot[1][0]*scale,  rot[1][1]*scale,  rot[1][2]*scale,
            rot[2][0]*scale,  rot[2][1]*scale,  rot[2][2]*scale]
        offset_vector = self._alignSettings['offset']
        transformation_matrix = [rotationScale[0], rotationScale[1], rotationScale[2], offset_vector[0],
                                 rotationScale[3], rotationScale[4], rotationScale[5], offset_vector[1],
                                 rotationScale[6], rotationScale[7], rotationScale[8], offset_vector[2],
                                 0.0,              0.0,              0.0,              1.0]
        self._scene.setTransformationMatrix(transformation_matrix)
        if self._alignSettingsChangeCallback is not None:
            self._alignSettingsChangeCallback()

    def _clear(self):
        """
        Ensure scene for this region is not in use before calling!
        """
        self._scene = None
        self._alignSettingsChangeCallback = None
        self._resetAlignSettings()
        self._isStateAlign = True
