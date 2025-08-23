# pylint: disable=C0103,C0302
import pytest
from pint import DimensionalityError

from pnpq.apt.protocol import (
    Address,
    AptMessage,
    AptMessage_MGMSG_HW_DISCONNECT,
    AptMessage_MGMSG_HW_GET_INFO,
    AptMessage_MGMSG_HW_REQ_INFO,
    AptMessage_MGMSG_HW_START_UPDATEMSGS,
    AptMessage_MGMSG_HW_STOP_UPDATEMSGS,
    AptMessage_MGMSG_MOD_GET_CHANENABLESTATE,
    AptMessage_MGMSG_MOD_IDENTIFY,
    AptMessage_MGMSG_MOD_REQ_CHANENABLESTATE,
    AptMessage_MGMSG_MOD_SET_CHANENABLESTATE,
    AptMessage_MGMSG_MOT_ACK_USTATUSUPDATE,
    AptMessage_MGMSG_MOT_GET_HOMEPARAMS,
    AptMessage_MGMSG_MOT_GET_JOGPARAMS,
    AptMessage_MGMSG_MOT_GET_POSCOUNTER,
    AptMessage_MGMSG_MOT_GET_STATUSUPDATE,
    AptMessage_MGMSG_MOT_GET_USTATUSUPDATE,
    AptMessage_MGMSG_MOT_GET_VELPARAMS,
    AptMessage_MGMSG_MOT_MOVE_ABSOLUTE,
    AptMessage_MGMSG_MOT_MOVE_COMPLETED,
    AptMessage_MGMSG_MOT_MOVE_COMPLETED_6_BYTES,
    AptMessage_MGMSG_MOT_MOVE_COMPLETED_20_BYTES,
    AptMessage_MGMSG_MOT_MOVE_HOME,
    AptMessage_MGMSG_MOT_MOVE_HOMED,
    AptMessage_MGMSG_MOT_MOVE_JOG,
    AptMessage_MGMSG_MOT_MOVE_STOP,
    AptMessage_MGMSG_MOT_MOVE_STOPPED,
    AptMessage_MGMSG_MOT_MOVE_STOPPED_6_BYTES,
    AptMessage_MGMSG_MOT_MOVE_STOPPED_20_BYTES,
    AptMessage_MGMSG_MOT_REQ_HOMEPARAMS,
    AptMessage_MGMSG_MOT_REQ_JOGPARAMS,
    AptMessage_MGMSG_MOT_REQ_POSCOUNTER,
    AptMessage_MGMSG_MOT_REQ_STATUSUPDATE,
    AptMessage_MGMSG_MOT_REQ_USTATUSUPDATE,
    AptMessage_MGMSG_MOT_REQ_VELPARAMS,
    AptMessage_MGMSG_MOT_SET_EEPROMPARAMS,
    AptMessage_MGMSG_MOT_SET_HOMEPARAMS,
    AptMessage_MGMSG_MOT_SET_JOGPARAMS,
    AptMessage_MGMSG_MOT_SET_POSCOUNTER,
    AptMessage_MGMSG_MOT_SET_VELPARAMS,
    AptMessage_MGMSG_POL_GET_PARAMS,
    AptMessage_MGMSG_POL_REQ_PARAMS,
    AptMessage_MGMSG_POL_SET_PARAMS,
    AptMessage_MGMSG_RESTOREFACTORYSETTINGS,
    AptMessageId,
    ChanIdent,
    EnableState,
    FirmwareVersion,
    HardwareType,
    HomeDirection,
    JogDirection,
    JogMode,
    LimitSwitch,
    Status,
    StopMode,
    UStatus,
)
from pnpq.units import pnpq_ureg


def test_AptMessage_MGMSG_HW_DISCONNECT_from_bytes() -> None:
    msg = AptMessage_MGMSG_HW_DISCONNECT.from_bytes(b"\x02\x00\x00\x00\x50\x01")
    assert msg.message_id == 0x0002
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_HW_DISCONNECT_to_bytes() -> None:
    msg = AptMessage_MGMSG_HW_DISCONNECT(
        destination=Address.GENERIC_USB, source=Address.HOST_CONTROLLER
    )
    assert msg.to_bytes() == b"\x02\x00\x00\x00\x50\x01"


def test_AptMessage_MGMSG_HW_GET_INFO_from_bytes() -> None:
    # Example message from official documentation, page 53 of issue
    # 37. The sample message doesn't match the example value for
    # modification state afterwards; we use the latter value here.
    msg = AptMessage_MGMSG_HW_GET_INFO.from_bytes(
        bytes.fromhex("0600 5400 81 22 89539A05 494F4E3030312000 2C00 02013900")
        + bytes(60)
        + bytes.fromhex("0100 0300 0100")
    )
    assert msg.message_id == 0x0006
    assert msg.destination == 0x01
    assert msg.source == 0x22
    assert msg.firmware_version == FirmwareVersion(
        major_revision=57,
        interim_revision=1,
        minor_revision=2,
        unused=0,
    )
    assert msg.hardware_type == HardwareType.BRUSHLESS_DC_CONTROLLER
    assert msg.hardware_version == 1
    assert msg.internal_use == bytes(60)
    assert msg.model_number == "ION001 "
    assert msg.modification_state == 3
    assert msg.number_of_channels == 1
    assert msg.serial_number == 94000009


def test_AptMessage_MGMSG_HW_GET_INFO_to_bytes() -> None:
    msg = AptMessage_MGMSG_HW_GET_INFO(
        destination=Address.HOST_CONTROLLER,
        source=Address.BAY_1,
        firmware_version=FirmwareVersion(
            major_revision=57,
            interim_revision=1,
            minor_revision=2,
            unused=0,
        ),
        hardware_type=HardwareType.BRUSHLESS_DC_CONTROLLER,
        hardware_version=1,
        internal_use=bytes(60),
        model_number="ION001 ",
        modification_state=3,
        number_of_channels=1,
        serial_number=94000009,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "0600 5400 81 22 89539A05 494F4E3030312000 2C00 02013900"
    ) + bytes(60) + bytes.fromhex("0100 0300 0100")


def test_AptMessage_MGMSG_HW_REQ_INFO_from_bytes() -> None:
    msg = AptMessage_MGMSG_HW_REQ_INFO.from_bytes(b"\x05\x00\x00\x00\x50\x01")
    assert msg.message_id == 0x0005
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_HW_REQ_INFO_to_bytes() -> None:
    msg = AptMessage_MGMSG_HW_REQ_INFO(
        destination=Address.GENERIC_USB, source=Address.HOST_CONTROLLER
    )
    assert msg.to_bytes() == b"\x05\x00\x00\x00\x50\x01"


def test_AptMessage_MGMSG_HW_START_UPDATEMSGS_from_bytes() -> None:
    msg = AptMessage_MGMSG_HW_START_UPDATEMSGS.from_bytes(b"\x11\x00\x00\x00\x50\x01")
    assert msg.message_id == 0x0011
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_HW_START_UPDATEMSGS_to_bytes() -> None:
    msg = AptMessage_MGMSG_HW_START_UPDATEMSGS(
        destination=Address.GENERIC_USB, source=Address.HOST_CONTROLLER
    )
    assert msg.to_bytes() == b"\x11\x00\x00\x00\x50\x01"


def test_AptMessage_MGMSG_HW_STOP_UPDATEMSGS_from_bytes() -> None:
    msg = AptMessage_MGMSG_HW_STOP_UPDATEMSGS.from_bytes(b"\x12\x00\x00\x00\x50\x01")
    assert msg.message_id == 0x0012
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_HW_STOP_UPDATEMSGS_to_bytes() -> None:
    msg = AptMessage_MGMSG_HW_STOP_UPDATEMSGS(
        destination=Address.GENERIC_USB, source=Address.HOST_CONTROLLER
    )
    assert msg.to_bytes() == b"\x12\x00\x00\x00\x50\x01"


def test_AptMessage_MGMSG_MOD_GET_CHANENABLESTATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_GET_CHANENABLESTATE.from_bytes(
        b"\x12\x02\x01\x02\x50\x01"
    )
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.enable_state == 0x02
    assert msg.message_id == 0x0212
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOD_GET_CHANENABLESTATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_GET_CHANENABLESTATE(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        enable_state=EnableState.CHANNEL_DISABLED,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x12\x02\x01\x02\x50\x01"


def test_AptMessage_MGMSG_MOD_REQ_CHANENABLESTATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_REQ_CHANENABLESTATE.from_bytes(
        b"\x11\x02\x01\x00\x50\x01"
    )
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0211
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOD_REQ_CHANENABLESTATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_REQ_CHANENABLESTATE(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x11\x02\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOD_SET_CHANENABLESTATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_SET_CHANENABLESTATE.from_bytes(
        b"\x10\x02\x01\x02\x50\x01"
    )
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.enable_state == 0x02
    assert msg.message_id == 0x0210
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOD_SET_CHANENABLESTATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_SET_CHANENABLESTATE(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        enable_state=EnableState.CHANNEL_DISABLED,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x10\x02\x01\x02\x50\x01"


def test_AptMessage_MGMSG_MOD_IDENTIFY_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_IDENTIFY.from_bytes(b"\x23\x02\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0223
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOD_IDENTIFY_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOD_IDENTIFY(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x23\x02\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_GET_POSCOUNTER_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_POSCOUNTER.from_bytes(
        bytes.fromhex("1204 0600 A2 01 0100400D0300")
    )

    assert msg.destination == 0x22
    assert msg.message_id == 0x0412
    assert msg.source == 0x01
    assert msg.chan_ident == 0x01
    assert msg.position == 200000


def test_AptMessage_MGMSG_MOT_GET_POSCOUNTER_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_POSCOUNTER(
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        chan_ident=ChanIdent.CHANNEL_1,
        position=200000,
    )
    assert msg.to_bytes() == bytes.fromhex("1204 0600 A2 01 0100400D0300")


def test_AptMessage_MGMSG_MOT_SET_POSCOUNTER_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_POSCOUNTER.from_bytes(
        bytes.fromhex("1004 0600 A2 01 0100400D0300")
    )

    # The official documentation's example refers to this as "Channel 2," but this is actually bay 1.
    assert msg.destination == 0x22

    assert msg.message_id == 0x0410
    assert msg.source == 0x01
    assert msg.chan_ident == 0x01
    assert msg.position == 200000


def test_AptMessage_MGMSG_MOT_SET_POSCOUNTER_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_POSCOUNTER(
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        chan_ident=ChanIdent.CHANNEL_1,
        position=200000,
    )
    assert msg.to_bytes() == bytes.fromhex("1004 0600 A2 01 0100400D0300")


def test_AptMessage_MGMSG_MOT_REQ_POSCOUNTER_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_POSCOUNTER.from_bytes(b"\x11\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.message_id == 0x0411
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_REQ_POSCOUNTER_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_POSCOUNTER(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x11\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_GET_STATUSUPDATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_STATUSUPDATE.from_bytes(
        bytes.fromhex("8104 0e00 81 22 0100 01000000 00000000 07000000")
    )
    assert msg.destination == 0x01
    assert msg.message_id == 0x0481
    assert msg.source == 0x22
    assert msg.position == 1
    assert msg.enc_count == 0
    assert msg.status == Status(CWHARDLIMIT=True, CCWHARDLIMIT=True, CWSOFTLIMIT=True)


def test_AptMessage_MGMSG_MOT_GET_STATUSUPDATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_STATUSUPDATE(
        destination=Address.HOST_CONTROLLER,
        source=Address.BAY_1,
        chan_ident=ChanIdent.CHANNEL_1,
        position=1,
        enc_count=0,
        status=Status(CWHARDLIMIT=True, CCWHARDLIMIT=True, CWSOFTLIMIT=True),
    )
    assert msg.to_bytes() == bytes.fromhex(
        "8104 0e00 81 22 0100 01000000 00000000 07000000"
    )


def test_AptMessage_MGMSG_MOT_REQ_STATUSUPDATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_STATUSUPDATE.from_bytes(b"\x80\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0480
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_REQ_STATUSUPDATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_STATUSUPDATE(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x80\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_ACK_USTATUSUPDATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_ACK_USTATUSUPDATE.from_bytes(b"\x92\x04\x00\x00\x50\x01")
    assert msg.destination == 0x50
    assert msg.message_id == 0x0492
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_ACK_USTATUSUPDATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_ACK_USTATUSUPDATE(
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x92\x04\x00\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_GET_USTATUSUPDATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_USTATUSUPDATE.from_bytes(
        bytes.fromhex("9104 0e00 81 22 0100 00000001 0001 FFFF 07000000")
    )
    assert msg.destination == 0x01
    assert msg.message_id == 0x0491
    assert msg.source == 0x22
    assert msg.position == 16777216
    assert msg.velocity == 256
    assert msg.motor_current == -1 * pnpq_ureg.milliamp
    assert msg.status == UStatus(CWHARDLIMIT=True, CCWHARDLIMIT=True, CWSOFTLIMIT=True)


def test_AptMessage_MGMSG_MOT_GET_USTATUSUPDATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_USTATUSUPDATE(
        destination=Address.HOST_CONTROLLER,
        source=Address.BAY_1,
        chan_ident=ChanIdent.CHANNEL_1,
        position=1,
        velocity=1,
        motor_current=(-1 * pnpq_ureg.milliamp),
        status=UStatus(CWHARDLIMIT=True, CCWHARDLIMIT=True, CWSOFTLIMIT=True),
    )
    assert msg.to_bytes() == bytes.fromhex(
        "9104 0e00 81 22 0100 01000000 0100 FFFF 07000000"
    )


def test_AptMessage_MGMSG_MOT_GET_USTATUSUPDATE_invalid_unit() -> None:
    with pytest.raises(DimensionalityError):
        AptMessage_MGMSG_MOT_GET_USTATUSUPDATE(
            destination=Address.HOST_CONTROLLER,
            source=Address.BAY_1,
            chan_ident=ChanIdent.CHANNEL_1,
            position=1,
            velocity=1,
            motor_current=(-1 * pnpq_ureg.meter),
            status=UStatus(CWHARDLIMIT=True, CCWHARDLIMIT=True, CWSOFTLIMIT=True),
        )


def test_AptMessage_MGMSG_MOT_REQ_USTATUSUPDATE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_USTATUSUPDATE.from_bytes(b"\x90\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0490
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_REQ_USTATUSUPDATE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_USTATUSUPDATE(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x90\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_MOVE_ABSOLUTE_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_ABSOLUTE.from_bytes(
        bytes.fromhex("5304 0600 A2 01 0100 400D0300")
    )
    assert msg.destination == 0x22
    assert msg.message_id == 0x0453
    assert msg.source == 0x01
    assert msg.chan_ident == 0x01
    assert msg.absolute_distance == 200000


def test_AptMessage_MGMSG_MOT_MOVE_ABSOLUTE_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_ABSOLUTE(
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        chan_ident=ChanIdent.CHANNEL_1,
        absolute_distance=200000,
    )
    assert msg.to_bytes() == bytes.fromhex("5304 0600 A2 01 0100 400D0300")


@pytest.mark.parametrize(
    "message_bytes, expected_length, expected_type",
    [
        ("6404 0100 01 22", 6, AptMessage_MGMSG_MOT_MOVE_COMPLETED_6_BYTES),
        (
            "6404 0e00 81 50 0100 68aaa001 0000 0000 30000080",
            20,
            AptMessage_MGMSG_MOT_MOVE_COMPLETED_20_BYTES,
        ),
    ],
)
def test_AptMessage_MGMSG_MOT_MOVE_COMPLETED_from_bytes(
    message_bytes: str, expected_length: int, expected_type: type[AptMessage]
) -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_COMPLETED.from_bytes(bytes.fromhex(message_bytes))
    assert (
        msg.data_length + 6 == expected_length
    )  # 6 bytes for the header which is not included in data_length
    assert isinstance(msg, expected_type)


def test_AptMessage_MGMSG_MOT_MOVE_COMPLETED_6_BYTES_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_COMPLETED_6_BYTES.from_bytes(
        bytes.fromhex("6404 0100 01 22")
    )
    assert msg.destination == 0x01
    assert msg.message_id == 0x0464
    assert msg.source == 0x22
    assert msg.chan_ident == 0x01


def test_AptMessage_MGMSG_MOT_MOVE_COMPLETED_6_BYTES_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_COMPLETED_6_BYTES(
        destination=Address.HOST_CONTROLLER,
        source=Address.BAY_1,
        chan_ident=ChanIdent.CHANNEL_1,
    )
    assert msg.to_bytes() == bytes.fromhex("6404 0100 01 22")


def test_AptMessage_MGMSG_MOT_MOVE_COMPLETED_20_BYTES_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_COMPLETED_20_BYTES.from_bytes(
        # Example message from testing with a real K10CR1 waveplate. Not seen on official documentation.
        bytes.fromhex("6404 0e00 81 50 0100 68aaa001 0000 0000 30000080")
    )
    assert msg.message_id == 0x0464
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x01
    assert msg.source == 0x50
    assert msg.position == 0x01A0AA68
    assert msg.velocity == 0x00
    assert msg.motor_current == 0x00
    assert msg.status == UStatus(INMOTIONCCW=True, INMOTIONCW=True, ENABLED=True)


def test_AptMessage_MGMSG_MOT_MOVE_COMPLETED_20_BYTES_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_COMPLETED_20_BYTES(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.HOST_CONTROLLER,
        source=Address.GENERIC_USB,
        position=0x01A0AA68,
        velocity=0x00,
        motor_current=0 * pnpq_ureg.milliamp,
        status=UStatus(INMOTIONCCW=True, INMOTIONCW=True, ENABLED=True),
    )
    assert msg.to_bytes() == bytes.fromhex(
        "6404 0e00 81 50 0100 68aaa001 0000 0000 30000080"
    )


def test_AptMessage_MGMSG_MOT_MOVE_HOME_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_HOME.from_bytes(b"\x43\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0443
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_MOVE_HOME_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_HOME(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x43\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_MOVE_HOMED_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_HOMED.from_bytes(b"\x44\x04\x01\x02\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0444
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_MOVE_HOMED_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_HOMED(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x44\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_POL_GET_PARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_POL_GET_PARAMS(
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
        velocity=50,
        home_position=0,
        jog_step_1=25,
        jog_step_2=25,
        jog_step_3=25,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "3205 0C00 D0 01 0000 3200 0000 1900 1900 1900"
    )


def test_AptMessage_MGMSG_POL_GET_PARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_POL_GET_PARAMS.from_bytes(
        bytes.fromhex("3205 0C00 D0 01 0000 3200 0000 1900 1900 1900")
    )
    assert msg.destination == 0x50
    assert msg.message_id == 0x0532
    assert msg.source == 0x01
    assert msg.unused == 0
    assert msg.velocity == 50
    assert msg.home_position == 0
    assert msg.jog_step_1 == 25
    assert msg.jog_step_2 == 25
    assert msg.jog_step_3 == 25


def test_AptMessage_AptMessage_MGMSG_POL_REQ_PARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_POL_REQ_PARAMS.from_bytes(b"\x31\x05\x00\x00\x50\x01")
    assert msg.destination == 0x50
    assert msg.message_id == 0x0531
    assert msg.source == 0x01


def test_AptMessage_AptMessage_MGMSG_POL_REQ_PARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_POL_REQ_PARAMS(
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x31\x05\x00\x00\x50\x01"


def test_AptMessage_MGMSG_POL_SET_PARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_POL_SET_PARAMS(
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
        velocity=50,
        home_position=0,
        jog_step_1=25,
        jog_step_2=25,
        jog_step_3=25,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "3005 0C00 D0 01 0000 3200 0000 1900 1900 1900"
    )


def test_AptMessage_MGMSG_POL_SET_PARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_POL_SET_PARAMS.from_bytes(
        bytes.fromhex("3005 0C00 D0 01 0000 3200 0000 1900 1900 1900")
    )
    assert msg.destination == 0x50
    assert msg.message_id == 0x0530
    assert msg.source == 0x01
    assert msg.unused == 0
    assert msg.velocity == 50
    assert msg.home_position == 0
    assert msg.jog_step_1 == 25
    assert msg.jog_step_2 == 25
    assert msg.jog_step_3 == 25


def test_AptMessage_MGMSG_MOT_MOVE_JOG_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_JOG.from_bytes(b"\x6a\x04\x01\x02\x01\x50")
    assert msg.message_id == 0x046A
    assert msg.chan_ident == 0x01
    assert msg.jog_direction == 0x02
    assert msg.destination == 0x01
    assert msg.source == 0x50


def test_AptMessage_MGMSG_MOT_MOVE_JOG_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_JOG(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        jog_direction=JogDirection.FORWARD,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x6a\x04\x01\x01\x50\x01"


def test_AptMessage_MGMSG_MOT_MOVE_STOP_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOP.from_bytes(b"\x65\x04\x01\x01\x50\x01")
    assert msg.message_id == 0x0465
    assert msg.chan_ident == 0x01
    assert msg.stop_mode == 0x01
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_MOVE_STOP_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOP(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        stop_mode=StopMode.IMMEDIATE,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x65\x04\x01\x01\x50\x01"


@pytest.mark.parametrize(
    "message_bytes, expected_length, expected_type",
    [
        ("6604 0100 01 22", 6, AptMessage_MGMSG_MOT_MOVE_STOPPED_6_BYTES),
        (
            "6604 0e00 81 50 0100 68aaa001 0000 0000 30000080",
            20,
            AptMessage_MGMSG_MOT_MOVE_STOPPED_20_BYTES,
        ),
    ],
)
def test_AptMessage_MGMSG_MOT_MOVE_STOPPED_from_bytes(
    message_bytes: str, expected_length: int, expected_type: type[AptMessage]
) -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOPPED.from_bytes(bytes.fromhex(message_bytes))
    assert (
        msg.data_length + 6 == expected_length
    )  # 6 bytes for the header which is not included in data_length
    assert isinstance(msg, expected_type)


def test_AptMessage_MGMSG_MOT_MOVE_STOPPED_6_BYTES_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOPPED_6_BYTES.from_bytes(
        bytes.fromhex("6604 0100 01 22")
    )
    assert msg.destination == 0x01
    assert msg.message_id == 0x0466
    assert msg.source == 0x22
    assert msg.chan_ident == 0x01


def test_AptMessage_MGMSG_MOT_MOVE_STOPPED_6_BYTES_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOPPED_6_BYTES(
        destination=Address.HOST_CONTROLLER,
        source=Address.BAY_1,
        chan_ident=ChanIdent.CHANNEL_1,
    )
    assert msg.to_bytes() == bytes.fromhex("6604 0100 01 22")


def test_AptMessage_MGMSG_MOT_MOVE_STOPPED_20_BYTES_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOPPED_20_BYTES.from_bytes(
        # Example message from testing with a real K10CR1 waveplate. Not seen on official documentation.
        bytes.fromhex("6604 0e00 81 50 0100 68aaa001 0000 0000 30000080")
    )
    assert msg.message_id == 0x0466
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x01
    assert msg.source == 0x50
    assert msg.position == 0x01A0AA68
    assert msg.velocity == 0x00
    assert msg.motor_current == 0x00
    assert msg.status == UStatus(INMOTIONCCW=True, INMOTIONCW=True, ENABLED=True)


def test_AptMessage_MGMSG_MOT_MOVE_STOPPED_20_BYTES_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_MOVE_STOPPED_20_BYTES(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.HOST_CONTROLLER,
        source=Address.GENERIC_USB,
        position=0x01A0AA68,
        velocity=0x00,
        motor_current=0 * pnpq_ureg.milliamp,
        status=UStatus(INMOTIONCCW=True, INMOTIONCW=True, ENABLED=True),
    )
    assert msg.to_bytes() == bytes.fromhex(
        "6604 0e00 81 50 0100 68aaa001 0000 0000 30000080"
    )


def test_AptMessage_MGMSG_RESTOREFACTORYSETTINGS_from_bytes() -> None:
    msg = AptMessage_MGMSG_RESTOREFACTORYSETTINGS.from_bytes(
        b"\x86\x06\x00\x00\x50\x01"
    )
    assert msg.message_id == 0x0686
    assert msg.destination == 0x50
    assert msg.source == 0x01


def test_AptMessage_MGMSG_RESTOREFACTORYSETTINGS_to_bytes() -> None:
    msg = AptMessage_MGMSG_RESTOREFACTORYSETTINGS(
        destination=Address.GENERIC_USB, source=Address.HOST_CONTROLLER
    )
    assert msg.to_bytes() == b"\x86\x06\x00\x00\x50\x01"


# We have not implemented any messages that are to be saved with SET_EEPROMPARAMS,
# so MGMSG_HW_GET_INFO will temporarily be used as the target for saving in this
# AptMessage_MGMSG_MOT_SET_EEPROMPARAMS unit test.
def test_AptMessage_MGMSG_MOT_SET_EEPROMPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_EEPROMPARAMS.from_bytes(
        bytes.fromhex("B904 0400 D0 01 0100 0600")
    )
    assert msg.destination == 0x50
    assert msg.message_id == 0x04B9
    assert msg.source == 0x01
    assert msg.chan_ident == 0x01
    assert msg.message_id_to_save == 0x0006


def test_AptMessage_MGMSG_MOT_SET_EEPROMPARAMS_to_bytes() -> None:

    msg = AptMessage_MGMSG_MOT_SET_EEPROMPARAMS(
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
        chan_ident=ChanIdent.CHANNEL_1,
        message_id_to_save=AptMessageId.MGMSG_HW_GET_INFO,
    )
    assert msg.to_bytes() == bytes.fromhex("B904 0400 D0 01 0100 0600")


def test_AptMessage_MGMSG_MOT_SET_VELPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_VELPARAMS.from_bytes(
        bytes.fromhex("1304 0E00 A2 01 0100 00000000 B0350000 CDCCCC00")
    )
    assert msg.destination == 0x22
    assert msg.message_id == 0x0413
    assert msg.source == 0x01
    assert msg.chan_ident == 0x01
    assert msg.minimum_velocity == 0x00000000
    assert msg.acceleration == 0x000035B0
    assert msg.maximum_velocity == 0x00CCCCCD


def test_AptMessage_MGMSG_MOT_SET_VELPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_VELPARAMS(
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        chan_ident=ChanIdent.CHANNEL_1,
        minimum_velocity=0x00000000,
        acceleration=0x000035B0,
        maximum_velocity=0x00CCCCCD,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "1304 0E00 A2 01 0100 00000000 B0350000 CDCCCC00"
    )


def test_AptMessage_MGMSG_MOT_GET_VELPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_VELPARAMS.from_bytes(
        bytes.fromhex("1504 0E00 A2 01 0100 00000000 B0350000 CDCCCC00")
    )
    assert msg.destination == 0x22
    assert msg.message_id == 0x0415
    assert msg.source == 0x01
    assert msg.chan_ident == 0x01
    assert msg.minimum_velocity == 0x00000000
    assert msg.acceleration == 0x000035B0
    assert msg.maximum_velocity == 0x00CCCCCD


def test_AptMessage_MGMSG_MOT_GET_VELPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_VELPARAMS(
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        chan_ident=ChanIdent.CHANNEL_1,
        minimum_velocity=0x00000000,
        acceleration=0x000035B0,
        maximum_velocity=0x00CCCCCD,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "1504 0E00 A2 01 0100 00000000 B0350000 CDCCCC00"
    )


def test_AptMessage_MGMSG_MOT_REQ_VELPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_VELPARAMS.from_bytes(b"\x14\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0414
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_REQ_VELPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_VELPARAMS(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x14\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_SET_JOGPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_JOGPARAMS.from_bytes(
        bytes.fromhex(
            "1604 1600 A2 01 0100 0100 E8030000 00000000 B0350000 CDCCCC00 0200"
        )
    )

    assert msg.chan_ident == ChanIdent.CHANNEL_1
    assert msg.destination == 0x22
    assert msg.message_id == 0x0416
    assert msg.source == 0x01
    assert msg.jog_mode == JogMode.CONTINUOUS
    assert msg.jog_step_size == 1000
    assert msg.jog_minimum_velocity == 0x00000000
    assert msg.jog_acceleration == 0x000035B0
    assert msg.jog_maximum_velocity == 0x00CCCCCD
    assert msg.jog_stop_mode == StopMode.CONTROLLED


def test_AptMessage_MGMSG_MOT_SET_JOGPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_JOGPARAMS(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        jog_mode=JogMode.CONTINUOUS,
        jog_step_size=1000,
        jog_minimum_velocity=0x00000000,
        jog_acceleration=0x000035B0,
        jog_maximum_velocity=0x00CCCCCD,
        jog_stop_mode=StopMode.CONTROLLED,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "1604 1600 A2 01 0100 0100 E8030000 00000000 B0350000 CDCCCC00 0200"
    )


def test_AptMessage_MGMSG_MOT_GET_JOGPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_JOGPARAMS.from_bytes(
        bytes.fromhex(
            "1804 1600 A2 01 0100 0100 E8030000 00000000 B0350000 CDCCCC00 0200"
        )
    )

    assert msg.chan_ident == ChanIdent.CHANNEL_1
    assert msg.destination == 0x22
    assert msg.message_id == 0x0418
    assert msg.source == 0x01
    assert msg.jog_mode == JogMode.CONTINUOUS
    assert msg.jog_step_size == 1000
    assert msg.jog_minimum_velocity == 0x00000000
    assert msg.jog_acceleration == 0x000035B0
    assert msg.jog_maximum_velocity == 0x00CCCCCD
    assert msg.jog_stop_mode == StopMode.CONTROLLED


def test_AptMessage_MGMSG_MOT_GET_JOGPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_JOGPARAMS(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        jog_mode=JogMode.CONTINUOUS,
        jog_step_size=1000,
        jog_minimum_velocity=0x00000000,
        jog_acceleration=0x000035B0,
        jog_maximum_velocity=0x00CCCCCD,
        jog_stop_mode=StopMode.CONTROLLED,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "1804 1600 A2 01 0100 0100 E8030000 00000000 B0350000 CDCCCC00 0200"
    )


def test_AptMessage_MGMSG_MOT_REQ_JOGPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_JOGPARAMS.from_bytes(b"\x17\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0417
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_REQ_JOGPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_JOGPARAMS(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.GENERIC_USB,
        source=Address.HOST_CONTROLLER,
    )
    assert msg.to_bytes() == b"\x17\x04\x01\x00\x50\x01"


def test_AptMessage_MGMSG_MOT_SET_HOMEPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_HOMEPARAMS.from_bytes(
        bytes.fromhex("4004 0E00 A201 0100 0000 0000 33333300 00000000")
    )

    assert msg.chan_ident == ChanIdent.CHANNEL_1
    assert msg.destination == 0x22
    assert msg.message_id == 0x0440
    assert msg.source == 0x01
    assert msg.home_direction == 0x00
    assert msg.limit_switch == 0x00
    assert msg.home_velocity == 0x00333333
    assert msg.offset_distance == 0x00000000


def test_AptMessage_MGMSG_MOT_SET_HOMEPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_SET_HOMEPARAMS(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        home_direction=HomeDirection.FORWARD_0,
        limit_switch=LimitSwitch.NULL,
        home_velocity=0x00333333,
        offset_distance=0x00000000,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "4004 0E00 A201 0100 0000 0000 33333300 00000000"
    )


def test_AptMessage_MGMSG_MOT_GET_HOMEPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_HOMEPARAMS.from_bytes(
        bytes.fromhex("4204 0E00 A201 0100 0000 0000 33333300 00000000")
    )

    assert msg.chan_ident == ChanIdent.CHANNEL_1
    assert msg.destination == 0x22
    assert msg.message_id == 0x0442
    assert msg.source == 0x01
    assert msg.home_direction == 0x00
    assert msg.limit_switch == 0x00
    assert msg.home_velocity == 0x00333333
    assert msg.offset_distance == 0x00000000


def test_AptMessage_MGMSG_MOT_REQ_HOMEPARAMS_from_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_REQ_HOMEPARAMS.from_bytes(b"\x41\x04\x01\x00\x50\x01")
    assert msg.chan_ident == 0x01
    assert msg.destination == 0x50
    assert msg.message_id == 0x0441
    assert msg.source == 0x01


def test_AptMessage_MGMSG_MOT_GET_HOMEPARAMS_to_bytes() -> None:
    msg = AptMessage_MGMSG_MOT_GET_HOMEPARAMS(
        chan_ident=ChanIdent.CHANNEL_1,
        destination=Address.BAY_1,
        source=Address.HOST_CONTROLLER,
        home_direction=HomeDirection.FORWARD_0,
        limit_switch=LimitSwitch.NULL,
        home_velocity=0x00333333,
        offset_distance=0x00000000,
    )
    assert msg.to_bytes() == bytes.fromhex(
        "4204 0E00 A201 0100 0000 0000 33333300 00000000"
    )


@pytest.mark.parametrize(
    "chan_ident_int, expected_channel",
    [
        (1, ChanIdent.CHANNEL_1),
        (2, ChanIdent.CHANNEL_2),
        (3, ChanIdent.CHANNEL_3),
        (4, ChanIdent.CHANNEL_4),
    ],
)
def test_ChanIdent_init(chan_ident_int: int, expected_channel: ChanIdent) -> None:
    chan_ident = ChanIdent.from_linear(chan_ident_int)
    assert chan_ident == expected_channel
