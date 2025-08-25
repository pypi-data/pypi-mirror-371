# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import BinaryIO, Dict, List


class AbstractEcommerceVideoRequest(TeaModel):
    def __init__(
        self,
        duration: float = None,
        height: int = None,
        video_url: str = None,
        width: int = None,
    ):
        # This parameter is required.
        self.duration = duration
        self.height = height
        # This parameter is required.
        self.video_url = video_url
        self.width = width

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.duration is not None:
            result['Duration'] = self.duration
        if self.height is not None:
            result['Height'] = self.height
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        if self.width is not None:
            result['Width'] = self.width
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Duration') is not None:
            self.duration = m.get('Duration')
        if m.get('Height') is not None:
            self.height = m.get('Height')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        if m.get('Width') is not None:
            self.width = m.get('Width')
        return self


class AbstractEcommerceVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        duration: float = None,
        height: int = None,
        video_url_object: BinaryIO = None,
        width: int = None,
    ):
        # This parameter is required.
        self.duration = duration
        self.height = height
        # This parameter is required.
        self.video_url_object = video_url_object
        self.width = width

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.duration is not None:
            result['Duration'] = self.duration
        if self.height is not None:
            result['Height'] = self.height
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        if self.width is not None:
            result['Width'] = self.width
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Duration') is not None:
            self.duration = m.get('Duration')
        if m.get('Height') is not None:
            self.height = m.get('Height')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        if m.get('Width') is not None:
            self.width = m.get('Width')
        return self


class AbstractEcommerceVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_cover_url: str = None,
        video_url: str = None,
    ):
        self.video_cover_url = video_cover_url
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_cover_url is not None:
            result['VideoCoverUrl'] = self.video_cover_url
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoCoverUrl') is not None:
            self.video_cover_url = m.get('VideoCoverUrl')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class AbstractEcommerceVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: AbstractEcommerceVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = AbstractEcommerceVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class AbstractEcommerceVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AbstractEcommerceVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AbstractEcommerceVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AbstractFilmVideoRequest(TeaModel):
    def __init__(
        self,
        length: int = None,
        video_url: str = None,
    ):
        # This parameter is required.
        self.length = length
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.length is not None:
            result['Length'] = self.length
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Length') is not None:
            self.length = m.get('Length')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class AbstractFilmVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        length: int = None,
        video_url_object: BinaryIO = None,
    ):
        # This parameter is required.
        self.length = length
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.length is not None:
            result['Length'] = self.length
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Length') is not None:
            self.length = m.get('Length')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class AbstractFilmVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class AbstractFilmVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: AbstractFilmVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = AbstractFilmVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class AbstractFilmVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AbstractFilmVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AbstractFilmVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AddFaceVideoTemplateRequest(TeaModel):
    def __init__(
        self,
        video_scene: str = None,
        video_url: str = None,
    ):
        self.video_scene = video_scene
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_scene is not None:
            result['VideoScene'] = self.video_scene
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoScene') is not None:
            self.video_scene = m.get('VideoScene')
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class AddFaceVideoTemplateAdvanceRequest(TeaModel):
    def __init__(
        self,
        video_scene: str = None,
        video_urlobject: BinaryIO = None,
    ):
        self.video_scene = video_scene
        # This parameter is required.
        self.video_urlobject = video_urlobject

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_scene is not None:
            result['VideoScene'] = self.video_scene
        if self.video_urlobject is not None:
            result['VideoURL'] = self.video_urlobject
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoScene') is not None:
            self.video_scene = m.get('VideoScene')
        if m.get('VideoURL') is not None:
            self.video_urlobject = m.get('VideoURL')
        return self


class AddFaceVideoTemplateResponseBodyDateFaceInfos(TeaModel):
    def __init__(
        self,
        template_face_id: str = None,
        template_face_url: str = None,
    ):
        self.template_face_id = template_face_id
        self.template_face_url = template_face_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.template_face_id is not None:
            result['TemplateFaceID'] = self.template_face_id
        if self.template_face_url is not None:
            result['TemplateFaceURL'] = self.template_face_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('TemplateFaceID') is not None:
            self.template_face_id = m.get('TemplateFaceID')
        if m.get('TemplateFaceURL') is not None:
            self.template_face_url = m.get('TemplateFaceURL')
        return self


class AddFaceVideoTemplateResponseBodyDate(TeaModel):
    def __init__(
        self,
        face_infos: List[AddFaceVideoTemplateResponseBodyDateFaceInfos] = None,
        template_id: str = None,
        trans_result: str = None,
    ):
        self.face_infos = face_infos
        self.template_id = template_id
        self.trans_result = trans_result

    def validate(self):
        if self.face_infos:
            for k in self.face_infos:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['FaceInfos'] = []
        if self.face_infos is not None:
            for k in self.face_infos:
                result['FaceInfos'].append(k.to_map() if k else None)
        if self.template_id is not None:
            result['TemplateId'] = self.template_id
        if self.trans_result is not None:
            result['TransResult'] = self.trans_result
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.face_infos = []
        if m.get('FaceInfos') is not None:
            for k in m.get('FaceInfos'):
                temp_model = AddFaceVideoTemplateResponseBodyDateFaceInfos()
                self.face_infos.append(temp_model.from_map(k))
        if m.get('TemplateId') is not None:
            self.template_id = m.get('TemplateId')
        if m.get('TransResult') is not None:
            self.trans_result = m.get('TransResult')
        return self


class AddFaceVideoTemplateResponseBody(TeaModel):
    def __init__(
        self,
        date: AddFaceVideoTemplateResponseBodyDate = None,
        message: str = None,
        request_id: str = None,
    ):
        self.date = date
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.date:
            self.date.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.date is not None:
            result['Date'] = self.date.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Date') is not None:
            temp_model = AddFaceVideoTemplateResponseBodyDate()
            self.date = temp_model.from_map(m['Date'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class AddFaceVideoTemplateResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AddFaceVideoTemplateResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AddFaceVideoTemplateResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AdjustVideoColorRequest(TeaModel):
    def __init__(
        self,
        mode: str = None,
        video_bitrate: int = None,
        video_codec: str = None,
        video_format: str = None,
        video_url: str = None,
    ):
        self.mode = mode
        self.video_bitrate = video_bitrate
        self.video_codec = video_codec
        self.video_format = video_format
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.mode is not None:
            result['Mode'] = self.mode
        if self.video_bitrate is not None:
            result['VideoBitrate'] = self.video_bitrate
        if self.video_codec is not None:
            result['VideoCodec'] = self.video_codec
        if self.video_format is not None:
            result['VideoFormat'] = self.video_format
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Mode') is not None:
            self.mode = m.get('Mode')
        if m.get('VideoBitrate') is not None:
            self.video_bitrate = m.get('VideoBitrate')
        if m.get('VideoCodec') is not None:
            self.video_codec = m.get('VideoCodec')
        if m.get('VideoFormat') is not None:
            self.video_format = m.get('VideoFormat')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class AdjustVideoColorAdvanceRequest(TeaModel):
    def __init__(
        self,
        mode: str = None,
        video_bitrate: int = None,
        video_codec: str = None,
        video_format: str = None,
        video_url_object: BinaryIO = None,
    ):
        self.mode = mode
        self.video_bitrate = video_bitrate
        self.video_codec = video_codec
        self.video_format = video_format
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.mode is not None:
            result['Mode'] = self.mode
        if self.video_bitrate is not None:
            result['VideoBitrate'] = self.video_bitrate
        if self.video_codec is not None:
            result['VideoCodec'] = self.video_codec
        if self.video_format is not None:
            result['VideoFormat'] = self.video_format
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Mode') is not None:
            self.mode = m.get('Mode')
        if m.get('VideoBitrate') is not None:
            self.video_bitrate = m.get('VideoBitrate')
        if m.get('VideoCodec') is not None:
            self.video_codec = m.get('VideoCodec')
        if m.get('VideoFormat') is not None:
            self.video_format = m.get('VideoFormat')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class AdjustVideoColorResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class AdjustVideoColorResponseBody(TeaModel):
    def __init__(
        self,
        data: AdjustVideoColorResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = AdjustVideoColorResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class AdjustVideoColorResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AdjustVideoColorResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AdjustVideoColorResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ChangeVideoSizeRequest(TeaModel):
    def __init__(
        self,
        b: int = None,
        crop_type: str = None,
        fill_type: str = None,
        g: int = None,
        height: int = None,
        r: int = None,
        tightness: float = None,
        video_url: str = None,
        width: int = None,
    ):
        self.b = b
        self.crop_type = crop_type
        self.fill_type = fill_type
        self.g = g
        # This parameter is required.
        self.height = height
        self.r = r
        self.tightness = tightness
        # This parameter is required.
        self.video_url = video_url
        # This parameter is required.
        self.width = width

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.b is not None:
            result['B'] = self.b
        if self.crop_type is not None:
            result['CropType'] = self.crop_type
        if self.fill_type is not None:
            result['FillType'] = self.fill_type
        if self.g is not None:
            result['G'] = self.g
        if self.height is not None:
            result['Height'] = self.height
        if self.r is not None:
            result['R'] = self.r
        if self.tightness is not None:
            result['Tightness'] = self.tightness
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        if self.width is not None:
            result['Width'] = self.width
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('B') is not None:
            self.b = m.get('B')
        if m.get('CropType') is not None:
            self.crop_type = m.get('CropType')
        if m.get('FillType') is not None:
            self.fill_type = m.get('FillType')
        if m.get('G') is not None:
            self.g = m.get('G')
        if m.get('Height') is not None:
            self.height = m.get('Height')
        if m.get('R') is not None:
            self.r = m.get('R')
        if m.get('Tightness') is not None:
            self.tightness = m.get('Tightness')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        if m.get('Width') is not None:
            self.width = m.get('Width')
        return self


class ChangeVideoSizeAdvanceRequest(TeaModel):
    def __init__(
        self,
        b: int = None,
        crop_type: str = None,
        fill_type: str = None,
        g: int = None,
        height: int = None,
        r: int = None,
        tightness: float = None,
        video_url_object: BinaryIO = None,
        width: int = None,
    ):
        self.b = b
        self.crop_type = crop_type
        self.fill_type = fill_type
        self.g = g
        # This parameter is required.
        self.height = height
        self.r = r
        self.tightness = tightness
        # This parameter is required.
        self.video_url_object = video_url_object
        # This parameter is required.
        self.width = width

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.b is not None:
            result['B'] = self.b
        if self.crop_type is not None:
            result['CropType'] = self.crop_type
        if self.fill_type is not None:
            result['FillType'] = self.fill_type
        if self.g is not None:
            result['G'] = self.g
        if self.height is not None:
            result['Height'] = self.height
        if self.r is not None:
            result['R'] = self.r
        if self.tightness is not None:
            result['Tightness'] = self.tightness
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        if self.width is not None:
            result['Width'] = self.width
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('B') is not None:
            self.b = m.get('B')
        if m.get('CropType') is not None:
            self.crop_type = m.get('CropType')
        if m.get('FillType') is not None:
            self.fill_type = m.get('FillType')
        if m.get('G') is not None:
            self.g = m.get('G')
        if m.get('Height') is not None:
            self.height = m.get('Height')
        if m.get('R') is not None:
            self.r = m.get('R')
        if m.get('Tightness') is not None:
            self.tightness = m.get('Tightness')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        if m.get('Width') is not None:
            self.width = m.get('Width')
        return self


class ChangeVideoSizeResponseBodyData(TeaModel):
    def __init__(
        self,
        video_cover_url: str = None,
        video_url: str = None,
    ):
        self.video_cover_url = video_cover_url
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_cover_url is not None:
            result['VideoCoverUrl'] = self.video_cover_url
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoCoverUrl') is not None:
            self.video_cover_url = m.get('VideoCoverUrl')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class ChangeVideoSizeResponseBody(TeaModel):
    def __init__(
        self,
        data: ChangeVideoSizeResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = ChangeVideoSizeResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class ChangeVideoSizeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ChangeVideoSizeResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ChangeVideoSizeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ConvertHdrVideoRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        hdrformat: str = None,
        max_illuminance: int = None,
        video_url: str = None,
    ):
        self.bitrate = bitrate
        self.hdrformat = hdrformat
        self.max_illuminance = max_illuminance
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.hdrformat is not None:
            result['HDRFormat'] = self.hdrformat
        if self.max_illuminance is not None:
            result['MaxIlluminance'] = self.max_illuminance
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('HDRFormat') is not None:
            self.hdrformat = m.get('HDRFormat')
        if m.get('MaxIlluminance') is not None:
            self.max_illuminance = m.get('MaxIlluminance')
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class ConvertHdrVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        hdrformat: str = None,
        max_illuminance: int = None,
        video_urlobject: BinaryIO = None,
    ):
        self.bitrate = bitrate
        self.hdrformat = hdrformat
        self.max_illuminance = max_illuminance
        # This parameter is required.
        self.video_urlobject = video_urlobject

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.hdrformat is not None:
            result['HDRFormat'] = self.hdrformat
        if self.max_illuminance is not None:
            result['MaxIlluminance'] = self.max_illuminance
        if self.video_urlobject is not None:
            result['VideoURL'] = self.video_urlobject
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('HDRFormat') is not None:
            self.hdrformat = m.get('HDRFormat')
        if m.get('MaxIlluminance') is not None:
            self.max_illuminance = m.get('MaxIlluminance')
        if m.get('VideoURL') is not None:
            self.video_urlobject = m.get('VideoURL')
        return self


class ConvertHdrVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class ConvertHdrVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: ConvertHdrVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = ConvertHdrVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class ConvertHdrVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ConvertHdrVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ConvertHdrVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteFaceVideoTemplateRequest(TeaModel):
    def __init__(
        self,
        template_id: str = None,
    ):
        # This parameter is required.
        self.template_id = template_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.template_id is not None:
            result['TemplateId'] = self.template_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('TemplateId') is not None:
            self.template_id = m.get('TemplateId')
        return self


class DeleteFaceVideoTemplateResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteFaceVideoTemplateResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteFaceVideoTemplateResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteFaceVideoTemplateResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class EnhancePortraitVideoRequest(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class EnhancePortraitVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        video_url_object: BinaryIO = None,
    ):
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class EnhancePortraitVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class EnhancePortraitVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: EnhancePortraitVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = EnhancePortraitVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class EnhancePortraitVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: EnhancePortraitVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = EnhancePortraitVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class EnhanceVideoQualityRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        frame_rate: int = None,
        hdrformat: str = None,
        max_illuminance: int = None,
        out_put_height: int = None,
        out_put_width: int = None,
        video_url: str = None,
    ):
        self.bitrate = bitrate
        self.frame_rate = frame_rate
        self.hdrformat = hdrformat
        self.max_illuminance = max_illuminance
        self.out_put_height = out_put_height
        self.out_put_width = out_put_width
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.frame_rate is not None:
            result['FrameRate'] = self.frame_rate
        if self.hdrformat is not None:
            result['HDRFormat'] = self.hdrformat
        if self.max_illuminance is not None:
            result['MaxIlluminance'] = self.max_illuminance
        if self.out_put_height is not None:
            result['OutPutHeight'] = self.out_put_height
        if self.out_put_width is not None:
            result['OutPutWidth'] = self.out_put_width
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('FrameRate') is not None:
            self.frame_rate = m.get('FrameRate')
        if m.get('HDRFormat') is not None:
            self.hdrformat = m.get('HDRFormat')
        if m.get('MaxIlluminance') is not None:
            self.max_illuminance = m.get('MaxIlluminance')
        if m.get('OutPutHeight') is not None:
            self.out_put_height = m.get('OutPutHeight')
        if m.get('OutPutWidth') is not None:
            self.out_put_width = m.get('OutPutWidth')
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class EnhanceVideoQualityAdvanceRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        frame_rate: int = None,
        hdrformat: str = None,
        max_illuminance: int = None,
        out_put_height: int = None,
        out_put_width: int = None,
        video_urlobject: BinaryIO = None,
    ):
        self.bitrate = bitrate
        self.frame_rate = frame_rate
        self.hdrformat = hdrformat
        self.max_illuminance = max_illuminance
        self.out_put_height = out_put_height
        self.out_put_width = out_put_width
        # This parameter is required.
        self.video_urlobject = video_urlobject

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.frame_rate is not None:
            result['FrameRate'] = self.frame_rate
        if self.hdrformat is not None:
            result['HDRFormat'] = self.hdrformat
        if self.max_illuminance is not None:
            result['MaxIlluminance'] = self.max_illuminance
        if self.out_put_height is not None:
            result['OutPutHeight'] = self.out_put_height
        if self.out_put_width is not None:
            result['OutPutWidth'] = self.out_put_width
        if self.video_urlobject is not None:
            result['VideoURL'] = self.video_urlobject
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('FrameRate') is not None:
            self.frame_rate = m.get('FrameRate')
        if m.get('HDRFormat') is not None:
            self.hdrformat = m.get('HDRFormat')
        if m.get('MaxIlluminance') is not None:
            self.max_illuminance = m.get('MaxIlluminance')
        if m.get('OutPutHeight') is not None:
            self.out_put_height = m.get('OutPutHeight')
        if m.get('OutPutWidth') is not None:
            self.out_put_width = m.get('OutPutWidth')
        if m.get('VideoURL') is not None:
            self.video_urlobject = m.get('VideoURL')
        return self


class EnhanceVideoQualityResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class EnhanceVideoQualityResponseBody(TeaModel):
    def __init__(
        self,
        data: EnhanceVideoQualityResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = EnhanceVideoQualityResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class EnhanceVideoQualityResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: EnhanceVideoQualityResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = EnhanceVideoQualityResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class EraseVideoLogoRequestBoxes(TeaModel):
    def __init__(
        self,
        h: float = None,
        w: float = None,
        x: float = None,
        y: float = None,
    ):
        self.h = h
        self.w = w
        self.x = x
        self.y = y

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.h is not None:
            result['H'] = self.h
        if self.w is not None:
            result['W'] = self.w
        if self.x is not None:
            result['X'] = self.x
        if self.y is not None:
            result['Y'] = self.y
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('H') is not None:
            self.h = m.get('H')
        if m.get('W') is not None:
            self.w = m.get('W')
        if m.get('X') is not None:
            self.x = m.get('X')
        if m.get('Y') is not None:
            self.y = m.get('Y')
        return self


class EraseVideoLogoRequest(TeaModel):
    def __init__(
        self,
        boxes: List[EraseVideoLogoRequestBoxes] = None,
        video_url: str = None,
    ):
        self.boxes = boxes
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        if self.boxes:
            for k in self.boxes:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['Boxes'] = []
        if self.boxes is not None:
            for k in self.boxes:
                result['Boxes'].append(k.to_map() if k else None)
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.boxes = []
        if m.get('Boxes') is not None:
            for k in m.get('Boxes'):
                temp_model = EraseVideoLogoRequestBoxes()
                self.boxes.append(temp_model.from_map(k))
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class EraseVideoLogoAdvanceRequestBoxes(TeaModel):
    def __init__(
        self,
        h: float = None,
        w: float = None,
        x: float = None,
        y: float = None,
    ):
        self.h = h
        self.w = w
        self.x = x
        self.y = y

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.h is not None:
            result['H'] = self.h
        if self.w is not None:
            result['W'] = self.w
        if self.x is not None:
            result['X'] = self.x
        if self.y is not None:
            result['Y'] = self.y
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('H') is not None:
            self.h = m.get('H')
        if m.get('W') is not None:
            self.w = m.get('W')
        if m.get('X') is not None:
            self.x = m.get('X')
        if m.get('Y') is not None:
            self.y = m.get('Y')
        return self


class EraseVideoLogoAdvanceRequest(TeaModel):
    def __init__(
        self,
        boxes: List[EraseVideoLogoAdvanceRequestBoxes] = None,
        video_url_object: BinaryIO = None,
    ):
        self.boxes = boxes
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        if self.boxes:
            for k in self.boxes:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['Boxes'] = []
        if self.boxes is not None:
            for k in self.boxes:
                result['Boxes'].append(k.to_map() if k else None)
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.boxes = []
        if m.get('Boxes') is not None:
            for k in m.get('Boxes'):
                temp_model = EraseVideoLogoAdvanceRequestBoxes()
                self.boxes.append(temp_model.from_map(k))
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class EraseVideoLogoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class EraseVideoLogoResponseBody(TeaModel):
    def __init__(
        self,
        data: EraseVideoLogoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = EraseVideoLogoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class EraseVideoLogoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: EraseVideoLogoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = EraseVideoLogoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class EraseVideoSubtitlesRequest(TeaModel):
    def __init__(
        self,
        bh: float = None,
        bw: float = None,
        bx: float = None,
        by: float = None,
        video_url: str = None,
    ):
        self.bh = bh
        self.bw = bw
        self.bx = bx
        self.by = by
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bh is not None:
            result['BH'] = self.bh
        if self.bw is not None:
            result['BW'] = self.bw
        if self.bx is not None:
            result['BX'] = self.bx
        if self.by is not None:
            result['BY'] = self.by
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('BH') is not None:
            self.bh = m.get('BH')
        if m.get('BW') is not None:
            self.bw = m.get('BW')
        if m.get('BX') is not None:
            self.bx = m.get('BX')
        if m.get('BY') is not None:
            self.by = m.get('BY')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class EraseVideoSubtitlesAdvanceRequest(TeaModel):
    def __init__(
        self,
        bh: float = None,
        bw: float = None,
        bx: float = None,
        by: float = None,
        video_url_object: BinaryIO = None,
    ):
        self.bh = bh
        self.bw = bw
        self.bx = bx
        self.by = by
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bh is not None:
            result['BH'] = self.bh
        if self.bw is not None:
            result['BW'] = self.bw
        if self.bx is not None:
            result['BX'] = self.bx
        if self.by is not None:
            result['BY'] = self.by
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('BH') is not None:
            self.bh = m.get('BH')
        if m.get('BW') is not None:
            self.bw = m.get('BW')
        if m.get('BX') is not None:
            self.bx = m.get('BX')
        if m.get('BY') is not None:
            self.by = m.get('BY')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class EraseVideoSubtitlesResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class EraseVideoSubtitlesResponseBody(TeaModel):
    def __init__(
        self,
        data: EraseVideoSubtitlesResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = EraseVideoSubtitlesResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class EraseVideoSubtitlesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: EraseVideoSubtitlesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = EraseVideoSubtitlesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GenerateHumanAnimeStyleVideoRequest(TeaModel):
    def __init__(
        self,
        cartoon_style: str = None,
        video_url: str = None,
    ):
        # This parameter is required.
        self.cartoon_style = cartoon_style
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cartoon_style is not None:
            result['CartoonStyle'] = self.cartoon_style
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CartoonStyle') is not None:
            self.cartoon_style = m.get('CartoonStyle')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class GenerateHumanAnimeStyleVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        cartoon_style: str = None,
        video_url_object: BinaryIO = None,
    ):
        # This parameter is required.
        self.cartoon_style = cartoon_style
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cartoon_style is not None:
            result['CartoonStyle'] = self.cartoon_style
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CartoonStyle') is not None:
            self.cartoon_style = m.get('CartoonStyle')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class GenerateHumanAnimeStyleVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class GenerateHumanAnimeStyleVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: GenerateHumanAnimeStyleVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = GenerateHumanAnimeStyleVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class GenerateHumanAnimeStyleVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GenerateHumanAnimeStyleVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GenerateHumanAnimeStyleVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GenerateVideoRequestFileList(TeaModel):
    def __init__(
        self,
        file_name: str = None,
        file_url: str = None,
        type: str = None,
    ):
        # This parameter is required.
        self.file_name = file_name
        # This parameter is required.
        self.file_url = file_url
        # This parameter is required.
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_name is not None:
            result['FileName'] = self.file_name
        if self.file_url is not None:
            result['FileUrl'] = self.file_url
        if self.type is not None:
            result['Type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('FileName') is not None:
            self.file_name = m.get('FileName')
        if m.get('FileUrl') is not None:
            self.file_url = m.get('FileUrl')
        if m.get('Type') is not None:
            self.type = m.get('Type')
        return self


class GenerateVideoRequest(TeaModel):
    def __init__(
        self,
        duration: float = None,
        duration_adaption: bool = None,
        file_list: List[GenerateVideoRequestFileList] = None,
        height: int = None,
        mute: bool = None,
        puzzle_effect: bool = None,
        scene: str = None,
        smart_effect: bool = None,
        style: str = None,
        transition_style: str = None,
        width: int = None,
    ):
        self.duration = duration
        self.duration_adaption = duration_adaption
        # 1
        # 
        # This parameter is required.
        self.file_list = file_list
        self.height = height
        self.mute = mute
        self.puzzle_effect = puzzle_effect
        self.scene = scene
        self.smart_effect = smart_effect
        self.style = style
        self.transition_style = transition_style
        self.width = width

    def validate(self):
        if self.file_list:
            for k in self.file_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.duration is not None:
            result['Duration'] = self.duration
        if self.duration_adaption is not None:
            result['DurationAdaption'] = self.duration_adaption
        result['FileList'] = []
        if self.file_list is not None:
            for k in self.file_list:
                result['FileList'].append(k.to_map() if k else None)
        if self.height is not None:
            result['Height'] = self.height
        if self.mute is not None:
            result['Mute'] = self.mute
        if self.puzzle_effect is not None:
            result['PuzzleEffect'] = self.puzzle_effect
        if self.scene is not None:
            result['Scene'] = self.scene
        if self.smart_effect is not None:
            result['SmartEffect'] = self.smart_effect
        if self.style is not None:
            result['Style'] = self.style
        if self.transition_style is not None:
            result['TransitionStyle'] = self.transition_style
        if self.width is not None:
            result['Width'] = self.width
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Duration') is not None:
            self.duration = m.get('Duration')
        if m.get('DurationAdaption') is not None:
            self.duration_adaption = m.get('DurationAdaption')
        self.file_list = []
        if m.get('FileList') is not None:
            for k in m.get('FileList'):
                temp_model = GenerateVideoRequestFileList()
                self.file_list.append(temp_model.from_map(k))
        if m.get('Height') is not None:
            self.height = m.get('Height')
        if m.get('Mute') is not None:
            self.mute = m.get('Mute')
        if m.get('PuzzleEffect') is not None:
            self.puzzle_effect = m.get('PuzzleEffect')
        if m.get('Scene') is not None:
            self.scene = m.get('Scene')
        if m.get('SmartEffect') is not None:
            self.smart_effect = m.get('SmartEffect')
        if m.get('Style') is not None:
            self.style = m.get('Style')
        if m.get('TransitionStyle') is not None:
            self.transition_style = m.get('TransitionStyle')
        if m.get('Width') is not None:
            self.width = m.get('Width')
        return self


class GenerateVideoAdvanceRequestFileList(TeaModel):
    def __init__(
        self,
        file_name: str = None,
        file_url_object: BinaryIO = None,
        type: str = None,
    ):
        # This parameter is required.
        self.file_name = file_name
        # This parameter is required.
        self.file_url_object = file_url_object
        # This parameter is required.
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_name is not None:
            result['FileName'] = self.file_name
        if self.file_url_object is not None:
            result['FileUrl'] = self.file_url_object
        if self.type is not None:
            result['Type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('FileName') is not None:
            self.file_name = m.get('FileName')
        if m.get('FileUrl') is not None:
            self.file_url_object = m.get('FileUrl')
        if m.get('Type') is not None:
            self.type = m.get('Type')
        return self


class GenerateVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        duration: float = None,
        duration_adaption: bool = None,
        file_list: List[GenerateVideoAdvanceRequestFileList] = None,
        height: int = None,
        mute: bool = None,
        puzzle_effect: bool = None,
        scene: str = None,
        smart_effect: bool = None,
        style: str = None,
        transition_style: str = None,
        width: int = None,
    ):
        self.duration = duration
        self.duration_adaption = duration_adaption
        # 1
        # 
        # This parameter is required.
        self.file_list = file_list
        self.height = height
        self.mute = mute
        self.puzzle_effect = puzzle_effect
        self.scene = scene
        self.smart_effect = smart_effect
        self.style = style
        self.transition_style = transition_style
        self.width = width

    def validate(self):
        if self.file_list:
            for k in self.file_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.duration is not None:
            result['Duration'] = self.duration
        if self.duration_adaption is not None:
            result['DurationAdaption'] = self.duration_adaption
        result['FileList'] = []
        if self.file_list is not None:
            for k in self.file_list:
                result['FileList'].append(k.to_map() if k else None)
        if self.height is not None:
            result['Height'] = self.height
        if self.mute is not None:
            result['Mute'] = self.mute
        if self.puzzle_effect is not None:
            result['PuzzleEffect'] = self.puzzle_effect
        if self.scene is not None:
            result['Scene'] = self.scene
        if self.smart_effect is not None:
            result['SmartEffect'] = self.smart_effect
        if self.style is not None:
            result['Style'] = self.style
        if self.transition_style is not None:
            result['TransitionStyle'] = self.transition_style
        if self.width is not None:
            result['Width'] = self.width
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Duration') is not None:
            self.duration = m.get('Duration')
        if m.get('DurationAdaption') is not None:
            self.duration_adaption = m.get('DurationAdaption')
        self.file_list = []
        if m.get('FileList') is not None:
            for k in m.get('FileList'):
                temp_model = GenerateVideoAdvanceRequestFileList()
                self.file_list.append(temp_model.from_map(k))
        if m.get('Height') is not None:
            self.height = m.get('Height')
        if m.get('Mute') is not None:
            self.mute = m.get('Mute')
        if m.get('PuzzleEffect') is not None:
            self.puzzle_effect = m.get('PuzzleEffect')
        if m.get('Scene') is not None:
            self.scene = m.get('Scene')
        if m.get('SmartEffect') is not None:
            self.smart_effect = m.get('SmartEffect')
        if m.get('Style') is not None:
            self.style = m.get('Style')
        if m.get('TransitionStyle') is not None:
            self.transition_style = m.get('TransitionStyle')
        if m.get('Width') is not None:
            self.width = m.get('Width')
        return self


class GenerateVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_cover_url: str = None,
        video_url: str = None,
    ):
        self.video_cover_url = video_cover_url
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_cover_url is not None:
            result['VideoCoverUrl'] = self.video_cover_url
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoCoverUrl') is not None:
            self.video_cover_url = m.get('VideoCoverUrl')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class GenerateVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: GenerateVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = GenerateVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class GenerateVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GenerateVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GenerateVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetAsyncJobResultRequest(TeaModel):
    def __init__(
        self,
        job_id: str = None,
    ):
        # This parameter is required.
        self.job_id = job_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.job_id is not None:
            result['JobId'] = self.job_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('JobId') is not None:
            self.job_id = m.get('JobId')
        return self


class GetAsyncJobResultResponseBodyData(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        job_id: str = None,
        result: str = None,
        status: str = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.job_id = job_id
        self.result = result
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['ErrorCode'] = self.error_code
        if self.error_message is not None:
            result['ErrorMessage'] = self.error_message
        if self.job_id is not None:
            result['JobId'] = self.job_id
        if self.result is not None:
            result['Result'] = self.result
        if self.status is not None:
            result['Status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ErrorCode') is not None:
            self.error_code = m.get('ErrorCode')
        if m.get('ErrorMessage') is not None:
            self.error_message = m.get('ErrorMessage')
        if m.get('JobId') is not None:
            self.job_id = m.get('JobId')
        if m.get('Result') is not None:
            self.result = m.get('Result')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        return self


class GetAsyncJobResultResponseBody(TeaModel):
    def __init__(
        self,
        data: GetAsyncJobResultResponseBodyData = None,
        request_id: str = None,
    ):
        self.data = data
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = GetAsyncJobResultResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class GetAsyncJobResultResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetAsyncJobResultResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetAsyncJobResultResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class InterpolateVideoFrameRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        frame_rate: int = None,
        video_url: str = None,
    ):
        self.bitrate = bitrate
        self.frame_rate = frame_rate
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.frame_rate is not None:
            result['FrameRate'] = self.frame_rate
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('FrameRate') is not None:
            self.frame_rate = m.get('FrameRate')
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class InterpolateVideoFrameAdvanceRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        frame_rate: int = None,
        video_urlobject: BinaryIO = None,
    ):
        self.bitrate = bitrate
        self.frame_rate = frame_rate
        # This parameter is required.
        self.video_urlobject = video_urlobject

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.frame_rate is not None:
            result['FrameRate'] = self.frame_rate
        if self.video_urlobject is not None:
            result['VideoURL'] = self.video_urlobject
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('FrameRate') is not None:
            self.frame_rate = m.get('FrameRate')
        if m.get('VideoURL') is not None:
            self.video_urlobject = m.get('VideoURL')
        return self


class InterpolateVideoFrameResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class InterpolateVideoFrameResponseBody(TeaModel):
    def __init__(
        self,
        data: InterpolateVideoFrameResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = InterpolateVideoFrameResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class InterpolateVideoFrameResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: InterpolateVideoFrameResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = InterpolateVideoFrameResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class MergeVideoFaceRequest(TeaModel):
    def __init__(
        self,
        add_watermark: bool = None,
        enhance: bool = None,
        reference_url: str = None,
        video_url: str = None,
        watermark_type: str = None,
    ):
        self.add_watermark = add_watermark
        self.enhance = enhance
        # This parameter is required.
        self.reference_url = reference_url
        # This parameter is required.
        self.video_url = video_url
        self.watermark_type = watermark_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_watermark is not None:
            result['AddWatermark'] = self.add_watermark
        if self.enhance is not None:
            result['Enhance'] = self.enhance
        if self.reference_url is not None:
            result['ReferenceURL'] = self.reference_url
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        if self.watermark_type is not None:
            result['WatermarkType'] = self.watermark_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AddWatermark') is not None:
            self.add_watermark = m.get('AddWatermark')
        if m.get('Enhance') is not None:
            self.enhance = m.get('Enhance')
        if m.get('ReferenceURL') is not None:
            self.reference_url = m.get('ReferenceURL')
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        if m.get('WatermarkType') is not None:
            self.watermark_type = m.get('WatermarkType')
        return self


class MergeVideoFaceAdvanceRequest(TeaModel):
    def __init__(
        self,
        add_watermark: bool = None,
        enhance: bool = None,
        reference_urlobject: BinaryIO = None,
        video_urlobject: BinaryIO = None,
        watermark_type: str = None,
    ):
        self.add_watermark = add_watermark
        self.enhance = enhance
        # This parameter is required.
        self.reference_urlobject = reference_urlobject
        # This parameter is required.
        self.video_urlobject = video_urlobject
        self.watermark_type = watermark_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_watermark is not None:
            result['AddWatermark'] = self.add_watermark
        if self.enhance is not None:
            result['Enhance'] = self.enhance
        if self.reference_urlobject is not None:
            result['ReferenceURL'] = self.reference_urlobject
        if self.video_urlobject is not None:
            result['VideoURL'] = self.video_urlobject
        if self.watermark_type is not None:
            result['WatermarkType'] = self.watermark_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AddWatermark') is not None:
            self.add_watermark = m.get('AddWatermark')
        if m.get('Enhance') is not None:
            self.enhance = m.get('Enhance')
        if m.get('ReferenceURL') is not None:
            self.reference_urlobject = m.get('ReferenceURL')
        if m.get('VideoURL') is not None:
            self.video_urlobject = m.get('VideoURL')
        if m.get('WatermarkType') is not None:
            self.watermark_type = m.get('WatermarkType')
        return self


class MergeVideoFaceResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class MergeVideoFaceResponseBody(TeaModel):
    def __init__(
        self,
        data: MergeVideoFaceResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = MergeVideoFaceResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class MergeVideoFaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: MergeVideoFaceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = MergeVideoFaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class MergeVideoModelFaceRequestMergeInfos(TeaModel):
    def __init__(
        self,
        image_url: str = None,
        template_face_id: str = None,
        template_face_url: str = None,
    ):
        self.image_url = image_url
        self.template_face_id = template_face_id
        self.template_face_url = template_face_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.image_url is not None:
            result['ImageURL'] = self.image_url
        if self.template_face_id is not None:
            result['TemplateFaceID'] = self.template_face_id
        if self.template_face_url is not None:
            result['TemplateFaceURL'] = self.template_face_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ImageURL') is not None:
            self.image_url = m.get('ImageURL')
        if m.get('TemplateFaceID') is not None:
            self.template_face_id = m.get('TemplateFaceID')
        if m.get('TemplateFaceURL') is not None:
            self.template_face_url = m.get('TemplateFaceURL')
        return self


class MergeVideoModelFaceRequest(TeaModel):
    def __init__(
        self,
        add_watermark: bool = None,
        enhance: bool = None,
        face_image_url: str = None,
        merge_infos: List[MergeVideoModelFaceRequestMergeInfos] = None,
        template_id: str = None,
        watermark_type: str = None,
    ):
        self.add_watermark = add_watermark
        self.enhance = enhance
        self.face_image_url = face_image_url
        self.merge_infos = merge_infos
        # This parameter is required.
        self.template_id = template_id
        self.watermark_type = watermark_type

    def validate(self):
        if self.merge_infos:
            for k in self.merge_infos:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_watermark is not None:
            result['AddWatermark'] = self.add_watermark
        if self.enhance is not None:
            result['Enhance'] = self.enhance
        if self.face_image_url is not None:
            result['FaceImageURL'] = self.face_image_url
        result['MergeInfos'] = []
        if self.merge_infos is not None:
            for k in self.merge_infos:
                result['MergeInfos'].append(k.to_map() if k else None)
        if self.template_id is not None:
            result['TemplateId'] = self.template_id
        if self.watermark_type is not None:
            result['WatermarkType'] = self.watermark_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AddWatermark') is not None:
            self.add_watermark = m.get('AddWatermark')
        if m.get('Enhance') is not None:
            self.enhance = m.get('Enhance')
        if m.get('FaceImageURL') is not None:
            self.face_image_url = m.get('FaceImageURL')
        self.merge_infos = []
        if m.get('MergeInfos') is not None:
            for k in m.get('MergeInfos'):
                temp_model = MergeVideoModelFaceRequestMergeInfos()
                self.merge_infos.append(temp_model.from_map(k))
        if m.get('TemplateId') is not None:
            self.template_id = m.get('TemplateId')
        if m.get('WatermarkType') is not None:
            self.watermark_type = m.get('WatermarkType')
        return self


class MergeVideoModelFaceAdvanceRequestMergeInfos(TeaModel):
    def __init__(
        self,
        image_url: str = None,
        template_face_id: str = None,
        template_face_url: str = None,
    ):
        self.image_url = image_url
        self.template_face_id = template_face_id
        self.template_face_url = template_face_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.image_url is not None:
            result['ImageURL'] = self.image_url
        if self.template_face_id is not None:
            result['TemplateFaceID'] = self.template_face_id
        if self.template_face_url is not None:
            result['TemplateFaceURL'] = self.template_face_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ImageURL') is not None:
            self.image_url = m.get('ImageURL')
        if m.get('TemplateFaceID') is not None:
            self.template_face_id = m.get('TemplateFaceID')
        if m.get('TemplateFaceURL') is not None:
            self.template_face_url = m.get('TemplateFaceURL')
        return self


class MergeVideoModelFaceAdvanceRequest(TeaModel):
    def __init__(
        self,
        add_watermark: bool = None,
        enhance: bool = None,
        face_image_urlobject: BinaryIO = None,
        merge_infos: List[MergeVideoModelFaceAdvanceRequestMergeInfos] = None,
        template_id: str = None,
        watermark_type: str = None,
    ):
        self.add_watermark = add_watermark
        self.enhance = enhance
        self.face_image_urlobject = face_image_urlobject
        self.merge_infos = merge_infos
        # This parameter is required.
        self.template_id = template_id
        self.watermark_type = watermark_type

    def validate(self):
        if self.merge_infos:
            for k in self.merge_infos:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_watermark is not None:
            result['AddWatermark'] = self.add_watermark
        if self.enhance is not None:
            result['Enhance'] = self.enhance
        if self.face_image_urlobject is not None:
            result['FaceImageURL'] = self.face_image_urlobject
        result['MergeInfos'] = []
        if self.merge_infos is not None:
            for k in self.merge_infos:
                result['MergeInfos'].append(k.to_map() if k else None)
        if self.template_id is not None:
            result['TemplateId'] = self.template_id
        if self.watermark_type is not None:
            result['WatermarkType'] = self.watermark_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AddWatermark') is not None:
            self.add_watermark = m.get('AddWatermark')
        if m.get('Enhance') is not None:
            self.enhance = m.get('Enhance')
        if m.get('FaceImageURL') is not None:
            self.face_image_urlobject = m.get('FaceImageURL')
        self.merge_infos = []
        if m.get('MergeInfos') is not None:
            for k in m.get('MergeInfos'):
                temp_model = MergeVideoModelFaceAdvanceRequestMergeInfos()
                self.merge_infos.append(temp_model.from_map(k))
        if m.get('TemplateId') is not None:
            self.template_id = m.get('TemplateId')
        if m.get('WatermarkType') is not None:
            self.watermark_type = m.get('WatermarkType')
        return self


class MergeVideoModelFaceResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class MergeVideoModelFaceResponseBody(TeaModel):
    def __init__(
        self,
        data: MergeVideoModelFaceResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = MergeVideoModelFaceResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class MergeVideoModelFaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: MergeVideoModelFaceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = MergeVideoModelFaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class QueryFaceVideoTemplateRequest(TeaModel):
    def __init__(
        self,
        page_no: int = None,
        page_size: int = None,
        template_id: str = None,
    ):
        self.page_no = page_no
        self.page_size = page_size
        self.template_id = template_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.page_no is not None:
            result['PageNo'] = self.page_no
        if self.page_size is not None:
            result['PageSize'] = self.page_size
        if self.template_id is not None:
            result['TemplateId'] = self.template_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('PageNo') is not None:
            self.page_no = m.get('PageNo')
        if m.get('PageSize') is not None:
            self.page_size = m.get('PageSize')
        if m.get('TemplateId') is not None:
            self.template_id = m.get('TemplateId')
        return self


class QueryFaceVideoTemplateResponseBodyDataElementsFaceInfos(TeaModel):
    def __init__(
        self,
        template_face_id: str = None,
        template_face_url: str = None,
    ):
        self.template_face_id = template_face_id
        self.template_face_url = template_face_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.template_face_id is not None:
            result['TemplateFaceID'] = self.template_face_id
        if self.template_face_url is not None:
            result['TemplateFaceURL'] = self.template_face_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('TemplateFaceID') is not None:
            self.template_face_id = m.get('TemplateFaceID')
        if m.get('TemplateFaceURL') is not None:
            self.template_face_url = m.get('TemplateFaceURL')
        return self


class QueryFaceVideoTemplateResponseBodyDataElements(TeaModel):
    def __init__(
        self,
        create_time: str = None,
        face_infos: List[QueryFaceVideoTemplateResponseBodyDataElementsFaceInfos] = None,
        template_id: str = None,
        template_url: str = None,
        update_time: str = None,
        user_id: str = None,
    ):
        self.create_time = create_time
        self.face_infos = face_infos
        self.template_id = template_id
        self.template_url = template_url
        self.update_time = update_time
        self.user_id = user_id

    def validate(self):
        if self.face_infos:
            for k in self.face_infos:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['CreateTime'] = self.create_time
        result['FaceInfos'] = []
        if self.face_infos is not None:
            for k in self.face_infos:
                result['FaceInfos'].append(k.to_map() if k else None)
        if self.template_id is not None:
            result['TemplateId'] = self.template_id
        if self.template_url is not None:
            result['TemplateURL'] = self.template_url
        if self.update_time is not None:
            result['UpdateTime'] = self.update_time
        if self.user_id is not None:
            result['UserId'] = self.user_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CreateTime') is not None:
            self.create_time = m.get('CreateTime')
        self.face_infos = []
        if m.get('FaceInfos') is not None:
            for k in m.get('FaceInfos'):
                temp_model = QueryFaceVideoTemplateResponseBodyDataElementsFaceInfos()
                self.face_infos.append(temp_model.from_map(k))
        if m.get('TemplateId') is not None:
            self.template_id = m.get('TemplateId')
        if m.get('TemplateURL') is not None:
            self.template_url = m.get('TemplateURL')
        if m.get('UpdateTime') is not None:
            self.update_time = m.get('UpdateTime')
        if m.get('UserId') is not None:
            self.user_id = m.get('UserId')
        return self


class QueryFaceVideoTemplateResponseBodyData(TeaModel):
    def __init__(
        self,
        elements: List[QueryFaceVideoTemplateResponseBodyDataElements] = None,
        total: int = None,
    ):
        self.elements = elements
        self.total = total

    def validate(self):
        if self.elements:
            for k in self.elements:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['Elements'] = []
        if self.elements is not None:
            for k in self.elements:
                result['Elements'].append(k.to_map() if k else None)
        if self.total is not None:
            result['Total'] = self.total
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.elements = []
        if m.get('Elements') is not None:
            for k in m.get('Elements'):
                temp_model = QueryFaceVideoTemplateResponseBodyDataElements()
                self.elements.append(temp_model.from_map(k))
        if m.get('Total') is not None:
            self.total = m.get('Total')
        return self


class QueryFaceVideoTemplateResponseBody(TeaModel):
    def __init__(
        self,
        data: QueryFaceVideoTemplateResponseBodyData = None,
        request_id: str = None,
    ):
        self.data = data
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = QueryFaceVideoTemplateResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class QueryFaceVideoTemplateResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: QueryFaceVideoTemplateResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = QueryFaceVideoTemplateResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ReduceVideoNoiseRequest(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class ReduceVideoNoiseAdvanceRequest(TeaModel):
    def __init__(
        self,
        video_url_object: BinaryIO = None,
    ):
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class ReduceVideoNoiseResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class ReduceVideoNoiseResponseBody(TeaModel):
    def __init__(
        self,
        data: ReduceVideoNoiseResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = ReduceVideoNoiseResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class ReduceVideoNoiseResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ReduceVideoNoiseResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ReduceVideoNoiseResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class SuperResolveVideoRequest(TeaModel):
    def __init__(
        self,
        bit_rate: int = None,
        video_url: str = None,
    ):
        self.bit_rate = bit_rate
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bit_rate is not None:
            result['BitRate'] = self.bit_rate
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('BitRate') is not None:
            self.bit_rate = m.get('BitRate')
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class SuperResolveVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        bit_rate: int = None,
        video_url_object: BinaryIO = None,
    ):
        self.bit_rate = bit_rate
        # This parameter is required.
        self.video_url_object = video_url_object

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bit_rate is not None:
            result['BitRate'] = self.bit_rate
        if self.video_url_object is not None:
            result['VideoUrl'] = self.video_url_object
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('BitRate') is not None:
            self.bit_rate = m.get('BitRate')
        if m.get('VideoUrl') is not None:
            self.video_url_object = m.get('VideoUrl')
        return self


class SuperResolveVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoUrl'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoUrl') is not None:
            self.video_url = m.get('VideoUrl')
        return self


class SuperResolveVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: SuperResolveVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = SuperResolveVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class SuperResolveVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: SuperResolveVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = SuperResolveVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ToneSdrVideoRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        recolor_model: str = None,
        video_url: str = None,
    ):
        self.bitrate = bitrate
        self.recolor_model = recolor_model
        # This parameter is required.
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.recolor_model is not None:
            result['RecolorModel'] = self.recolor_model
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('RecolorModel') is not None:
            self.recolor_model = m.get('RecolorModel')
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class ToneSdrVideoAdvanceRequest(TeaModel):
    def __init__(
        self,
        bitrate: int = None,
        recolor_model: str = None,
        video_urlobject: BinaryIO = None,
    ):
        self.bitrate = bitrate
        self.recolor_model = recolor_model
        # This parameter is required.
        self.video_urlobject = video_urlobject

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.bitrate is not None:
            result['Bitrate'] = self.bitrate
        if self.recolor_model is not None:
            result['RecolorModel'] = self.recolor_model
        if self.video_urlobject is not None:
            result['VideoURL'] = self.video_urlobject
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Bitrate') is not None:
            self.bitrate = m.get('Bitrate')
        if m.get('RecolorModel') is not None:
            self.recolor_model = m.get('RecolorModel')
        if m.get('VideoURL') is not None:
            self.video_urlobject = m.get('VideoURL')
        return self


class ToneSdrVideoResponseBodyData(TeaModel):
    def __init__(
        self,
        video_url: str = None,
    ):
        self.video_url = video_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.video_url is not None:
            result['VideoURL'] = self.video_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('VideoURL') is not None:
            self.video_url = m.get('VideoURL')
        return self


class ToneSdrVideoResponseBody(TeaModel):
    def __init__(
        self,
        data: ToneSdrVideoResponseBodyData = None,
        message: str = None,
        request_id: str = None,
    ):
        self.data = data
        self.message = message
        self.request_id = request_id

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['Data'] = self.data.to_map()
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Data') is not None:
            temp_model = ToneSdrVideoResponseBodyData()
            self.data = temp_model.from_map(m['Data'])
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class ToneSdrVideoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ToneSdrVideoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ToneSdrVideoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


