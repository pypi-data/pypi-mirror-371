import typing
from typing import Generic, Optional, TypeVar

from pydantic_xml import BaseXmlModel, element
from requests import Session


class SoapHeader(
    BaseXmlModel,
    tag="Header",
    ns="soap",
    nsmap={"soap": "http://schemas.xmlsoap.org/soap/envelope/"},
):
    """Base class for SOAP header."""


class SoapMethod(
    BaseXmlModel,
    tag="Method",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """Base class for SOAP method."""


MethodTypeT = TypeVar("MethodTypeT", bound=SoapMethod)


class SoapBody(
    BaseXmlModel,
    Generic[MethodTypeT],
    tag="Body",
    ns="soap",
):
    """SOAP body."""

    method: MethodTypeT


HeaderTypeT = TypeVar("HeaderTypeT", bound=SoapHeader)
BodyTypeT = TypeVar("BodyTypeT", bound=SoapBody)


class SoapEnvelopeNoHeader(
    BaseXmlModel,
    Generic[BodyTypeT],
    tag="Envelope",
    ns="soap",
    nsmap={
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    },
):
    """SOAP envelope."""

    body: BodyTypeT


class SoapEnvelope(
    BaseXmlModel,
    Generic[HeaderTypeT, BodyTypeT],
    tag="Envelope",
    ns="soap",
    nsmap={
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    },
):
    """SOAP envelope."""

    header: HeaderTypeT = element(default=None)
    body: BodyTypeT


class SoapResponse(
    SoapMethod,
    tag="Response",
    nsmap={"i": "http://www.w3.org/2001/XMLSchema-instance"},
):
    """Base class for SOAP response."""

    message: Optional[str] = element(
        tag="Message",
        ns="i",
        default=None,
    )


# pylint: disable=too-few-public-methods
class SoapyCon:
    """Base class for SOAP connection."""

    def __init__(self, session: Session, url: str):
        """
        Initialize the SoapyCon object
        :param session: The main connection session
        :param url: The URL to send the SOAP request to
        """
        self._session: Session = session
        self._url: str = url

    ReturnMethodT = TypeVar("ReturnMethodT", bound=SoapMethod)

    @typing.no_type_check
    def _send_command(
        self,
        header: Optional[SoapHeader],
        method: SoapMethod,
        return_method: typing.Type[ReturnMethodT],
        soap_action: Optional[str] = None,
        return_header=SoapHeader,
    ) -> ReturnMethodT:
        """
        Send a SOAP command
        :param header: The SOAP header object
        :param method: The SOAP method object
        :param return_method: The return SOAP method class
        :param soap_action: The optional SOAP action
        :param return_header: The return header class
        :return: The return method data
        """
        if soap_action is None:
            soap_action = method.__xml_tag__

        if header is None:
            request_shape = SoapEnvelopeNoHeader[SoapBody[type(method)]]
        else:
            request_shape = SoapEnvelope[
                type(header),
                SoapBody[type(method)],
            ]

        if return_header is None:
            return_shape = SoapEnvelopeNoHeader[return_method,]
        else:
            return_shape = SoapEnvelope[
                return_header,
                SoapBody[return_method],
            ]

        if header is None:
            envelope = request_shape(
                body=SoapBody(
                    method=method,
                ),
            )
        else:
            envelope = request_shape(
                header=header,
                body=SoapBody(
                    method=method,
                ),
            )

        headers = {
            "content-type": "text/xml",
            "SOAPAction": soap_action,
            "User-Agent": "Altium Designer",
        }

        response = self._session.post(self._url, data=envelope.to_xml(encoding="UTF-8"), headers=headers)

        if response.status_code != 200:
            raise ConnectionError(f'Failed to send "{soap_action}" command!')

        ret = return_shape.from_xml(response.text.encode("utf-8"))
        return ret.body.method
