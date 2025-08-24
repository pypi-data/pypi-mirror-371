from datetime import datetime
from io import BytesIO
from typing import Optional

from pydantic import BaseModel, field_validator


def parse_datetime(value):
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.fromisoformat(value)
    return datetime.fromtimestamp(value / 1000)


class CheckRequest(BaseModel):
    """Request model for checking a file or URL"""

    models: list[str]
    url: Optional[str] = None
    file: Optional[str] = None
    file_bytes: Optional[BytesIO] = None
    video_file: Optional[str] = None
    callback_url: Optional[str] = None
    params: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True


from typing import List

from pydantic import BaseModel, Field


class Request(BaseModel):
    id: str
    timestamp: float
    operations: int


class CleavageCategories(BaseModel):
    very_revealing: float
    revealing: float
    none: float


class MaleChestCategories(BaseModel):
    very_revealing: float
    revealing: float
    slightly_revealing: float
    none: float


class SuggestiveClasses(BaseModel):
    bikini: float
    cleavage: float
    cleavage_categories: CleavageCategories
    lingerie: float
    male_chest: float
    male_chest_categories: MaleChestCategories
    male_underwear: float
    miniskirt: float
    minishort: float
    nudity_art: float
    schematic: float
    sextoy: float
    suggestive_focus: float
    suggestive_pose: float
    swimwear_male: float
    swimwear_one_piece: float
    visibly_undressed: float
    other: float


class Context(BaseModel):
    sea_lake_pool: float
    outdoor_other: float
    indoor_other: float


class Nudity(BaseModel):
    sexual_activity: float
    sexual_display: float
    erotica: float
    very_suggestive: float
    suggestive: float
    mildly_suggestive: float
    suggestive_classes: SuggestiveClasses
    none: float
    context: Context


class Classes(BaseModel):
    firearm: float
    firearm_gesture: float
    firearm_toy: float
    knife: float


class FirearmType(BaseModel):
    animated: float


class FirearmAction(BaseModel):
    aiming_threat: float
    aiming_camera: float
    aiming_safe: float
    in_hand_not_aiming: float
    worn_not_in_hand: float
    not_worn: float


class Weapon(BaseModel):
    classes: Classes
    firearm_type: FirearmType
    firearm_action: FirearmAction


class Classes1(BaseModel):
    cannabis: float
    cannabis_logo_only: float
    cannabis_plant: float
    cannabis_drug: float
    recreational_drugs_not_cannabis: float


class RecreationalDrug(BaseModel):
    prob: float
    classes: Classes1


class Classes2(BaseModel):
    pills: float
    paraphernalia: float


class Medical(BaseModel):
    prob: float
    classes: Classes2


class Alcohol(BaseModel):
    prob: float


class Dominant(BaseModel):
    r: int
    g: int
    b: int
    hex: str
    hsv: List[float]


class AccentItem(BaseModel):
    r: int
    g: int
    b: int
    hex: str
    hsv: List[float]


class OtherItem(BaseModel):
    r: int
    g: int
    b: int
    hex: str
    hsv: List[float]


class Colors(BaseModel):
    dominant: Dominant
    accent: List[AccentItem]
    other: List[OtherItem]


class Qr(BaseModel):
    personal: List
    link: List
    social: List
    spam: List
    profanity: List
    blacklist: List


class Type(BaseModel):
    photo: Optional[float] = None
    illustration: Optional[float] = None
    ai_generated: float
    ai_generators: Optional[dict[str, float]] # undocumented field


class Quality(BaseModel):
    score: float


class Offensive(BaseModel):
    nazi: float
    asian_swastika: float
    confederate: float
    supremacist: float
    terrorist: float
    middle_finger: float


class LeftEye(BaseModel):
    x: float
    y: float


class RightEye(BaseModel):
    x: float
    y: float


class NoseTip(BaseModel):
    x: float
    y: float


class LeftMouthCorner(BaseModel):
    x: float
    y: float


class RightMouthCorner(BaseModel):
    x: float
    y: float


class Features(BaseModel):
    left_eye: LeftEye
    right_eye: RightEye
    nose_tip: NoseTip
    left_mouth_corner: LeftMouthCorner
    right_mouth_corner: RightMouthCorner


class Attributes(BaseModel):
    minor: float
    sunglasses: float


class Face(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    features: Features
    attributes: Attributes


class Scam(BaseModel):
    prob: float


class Text(BaseModel):
    profanity: List
    personal: List
    link: List
    social: List
    extremism: List
    medical: List
    drug: List
    weapon: List
    content_trade: List = Field(..., alias="content-trade")
    money_transaction: List = Field(..., alias="money-transaction")
    spam: List
    violence: List
    self_harm: List = Field(..., alias="self-harm")
    has_artificial: float
    has_natural: float


class Classes3(BaseModel):
    very_bloody: float
    slightly_bloody: float
    body_organ: float
    serious_injury: float
    superficial_injury: float
    corpse: float
    skull: float
    unconscious: float
    body_waste: float
    other: float


class Type1(BaseModel):
    animated: float
    fake: float
    real: float


class Gore(BaseModel):
    prob: float
    classes: Classes3
    type: Type1


class Classes4(BaseModel):
    regular_tobacco: float
    ambiguous_tobacco: float


class Tobacco(BaseModel):
    prob: float
    classes: Classes4


class Classes5(BaseModel):
    physical_violence: float
    firearm_threat: float
    combat_sport: float


class Violence(BaseModel):
    prob: float
    classes: Classes5


class Type2(BaseModel):
    real: float
    fake: float
    animated: float


class SelfHarm(BaseModel):
    prob: float
    type: Type2


class Money(BaseModel):
    prob: float


class Gambling(BaseModel):
    prob: float


class Media(BaseModel):
    id: str
    uri: str


class CheckResponse(BaseModel):
    status: Optional[str] = None
    request: Optional[Request] = None
    nudity: Optional[Nudity] = None
    weapon: Optional[Weapon] = None
    recreational_drug: Optional[RecreationalDrug] = None
    medical: Optional[Medical] = None
    alcohol: Optional[Alcohol] = None
    sharpness: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    colors: Optional[Colors] = None
    qr: Optional[Qr] = None
    type: Optional[Type] = None
    quality: Optional[Quality] = None
    offensive: Optional[Offensive] = None
    faces: Optional[List[Face]] = None
    scam: Optional[Scam] = None
    text: Optional[Text] = None
    gore: Optional[Gore] = None
    tobacco: Optional[Tobacco] = None
    violence: Optional[Violence] = None
    self_harm: Optional[SelfHarm] = Field(None, alias="self-harm")
    money: Optional[Money] = None
    gambling: Optional[Gambling] = None
    media: Optional[Media] = None


# Video Async Response Models


class Request(BaseModel):
    id: str
    timestamp: float


class Media(BaseModel):
    id: str
    uri: str


class VideoAsyncResponse(BaseModel):
    status: str
    request: Request
    media: Media
    callback: str
