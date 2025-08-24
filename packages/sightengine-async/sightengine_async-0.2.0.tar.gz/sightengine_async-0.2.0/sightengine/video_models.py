from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Request(BaseModel):
    id: str
    timestamp: float
    operations: int


class Media(BaseModel):
    id: str
    uri: str


class Info(BaseModel):
    id: str
    position: int


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


class OtherItem(BaseModel):
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


class Colors(BaseModel):
    dominant: Dominant
    other: List[OtherItem]
    accent: Optional[List[AccentItem]] = None


class Qr(BaseModel):
    personal: List
    link: List
    social: List
    spam: List
    profanity: List
    blacklist: List


class Type(BaseModel):
    photo: float
    illustration: float
    ai_generated: float


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


class Frame(BaseModel):
    info: Info
    nudity: Nudity
    weapon: Weapon
    recreational_drug: RecreationalDrug
    medical: Medical
    alcohol: Alcohol
    sharpness: float
    brightness: float
    contrast: float
    colors: Colors
    qr: Qr
    type: Type
    quality: Quality
    offensive: Offensive
    faces: List[Face]
    scam: Scam
    text: Text
    gore: Gore
    tobacco: Tobacco
    violence: Violence
    self_harm: SelfHarm = Field(..., alias="self-harm")
    money: Money
    gambling: Gambling


class Data(BaseModel):
    frames: List[Frame]


class VideoSyncResponse(BaseModel):
    status: str
    request: Request
    media: Media
    data: Data
