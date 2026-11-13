import os
from lxml import etree
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime
import base64

class XMLSigner:
    """Serviço para assinatura digital de XMLs com certificado A1/A3"""
    
    def __init__(self, cert_path: str, cert_password: str = None):
        """
        Args:
            cert_path: Caminho para arquivo .pfx ou .pem
            cert_password: Senha do certificado (se necessário)
        """
        self.cert_path = cert_path
        self.cert_password = cert_password.encode() if cert_password else None
        self._load_certificate()
    
    def _load_certificate(self):
        """Carrega certificado e chave privada"""
        with open(self.cert_path, 'rb') as f:
            cert_data = f.read()
        
        try:
            from cryptography.hazmat.primitives.serialization import pkcs12
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                cert_data, self.cert_password, backend=default_backend()
            )
            self.private_key = private_key
            self.certificate = certificate
        except Exception:
            raise ValueError(f"Erro ao carregar certificado: {self.cert_path}")
    
    def sign_xml(self, xml_string: str, reference_uri: str = "#NFe35240101234567000123550010000000011234567890") -> str:
        """
        Assina XML com certificado digital (XMLDSig)
        
        Args:
            xml_string: XML em string
            reference_uri: URI da referência (padrão: #NFe...)
        
        Returns:
            XML assinado em string
        """
        root = etree.fromstring(xml_string.encode('utf-8'))
        
        # Criar elemento Signature
        sig_ns = "http://www.w3.org/2000/09/xmldsig#"
        sig_elem = etree.Element(f"{{{sig_ns}}}Signature", Id="NFe35240101234567000123550010000000011234567890")
        
        # SignedInfo
        signed_info = etree.SubElement(sig_elem, f"{{{sig_ns}}}SignedInfo")
        etree.SubElement(signed_info, f"{{{sig_ns}}}CanonicalizationMethod", Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")
        etree.SubElement(signed_info, f"{{{sig_ns}}}SignatureMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1")
        
        # Reference
        reference = etree.SubElement(signed_info, f"{{{sig_ns}}}Reference", URI=reference_uri)
        transforms = etree.SubElement(reference, f"{{{sig_ns}}}Transforms")
        etree.SubElement(transforms, f"{{{sig_ns}}}Transform", Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature")
        etree.SubElement(transforms, f"{{{sig_ns}}}Transform", Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")
        etree.SubElement(reference, f"{{{sig_ns}}}DigestMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#sha1")
        
        # Calcular digest
        xml_bytes = etree.tostring(root, method='c14n')
        digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
        digest.update(xml_bytes)
        digest_value = base64.b64encode(digest.finalize()).decode()
        etree.SubElement(reference, f"{{{sig_ns}}}DigestValue").text = digest_value
        
        # Assinar SignedInfo
        signed_info_bytes = etree.tostring(signed_info, method='c14n')
        signature_value = self.private_key.sign(
            signed_info_bytes,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        etree.SubElement(sig_elem, f"{{{sig_ns}}}SignatureValue").text = base64.b64encode(signature_value).decode()
        
        # KeyInfo com certificado
        key_info = etree.SubElement(sig_elem, f"{{{sig_ns}}}KeyInfo")
        x509_data = etree.SubElement(key_info, f"{{{sig_ns}}}X509Data")
        cert_pem = self.certificate.public_bytes(serialization.Encoding.PEM).decode()
        cert_b64 = base64.b64encode(self.certificate.public_bytes(serialization.Encoding.DER)).decode()
        etree.SubElement(x509_data, f"{{{sig_ns}}}X509Certificate").text = cert_b64
        
        # Adicionar Signature ao XML
        root.append(sig_elem)
        
        return etree.tostring(root, encoding='unicode', pretty_print=True)
