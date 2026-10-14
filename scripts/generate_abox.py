import re
import hashlib
import json
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from rdflib.namespace import XSD, OWL

EXA = Namespace("http://example.org/fraud/abox#")
EXT = Namespace("http://example.org/fraud/tbox#")


def create_rdf_from_json(json_data):
    g = Graph()

    g.bind("ext", EXT)
    g.bind("exa", EXA)
    g.bind("xsd", XSD)

    abox_iri = URIRef("http://example.org/fraud/abox")
    g.add((abox_iri, RDF.type, OWL.Ontology))
    g.add((abox_iri, OWL.imports, URIRef("http://example.org/fraud/tbox")))

    for customer in json_data:
        customer_uri = EXA[f"customer_{customer['id']}"]

        g.add((customer_uri, RDF.type, EXT.Customer))
        g.add(
            (
                customer_uri,
                EXT.fullName,
                Literal(customer["fullName"], datatype=XSD.string),
            )
        )
        g.add(
            (
                customer_uri,
                EXT.registrationDate,
                Literal(customer["registrationDate"], datatype=XSD.date),
            )
        )

        if customer["flaggedFraud"]:
            g.add((customer_uri, RDF.type, EXT.FraudulentCustomer))

        for iban in customer["ibans"]:
            iban_uri = EXA[f"iban_{iban.replace(' ', '').upper()}"]

            g.add((iban_uri, RDF.type, EXT.Iban))
            g.add((iban_uri, EXT.identifierValue, Literal(iban, datatype=XSD.string)))

            g.add((customer_uri, EXT.hasIban, iban_uri))

        for phone in customer["phones"]:
            phone_digits = re.sub(r"\D", "", phone)
            phone_uri = EXA[f"phone_{phone_digits}"]

            g.add((phone_uri, RDF.type, EXT.PhoneNumber))
            g.add((phone_uri, EXT.identifierValue, Literal(phone, datatype=XSD.string)))

            g.add((customer_uri, EXT.hasPhone, phone_uri))

        for email in customer["emails"]:
            email_uri = EXA[f"email_{hashlib.sha1(email.encode()).hexdigest()[:10]}"]

            g.add((email_uri, RDF.type, EXT.EmailAddress))
            g.add((email_uri, EXT.identifierValue, Literal(email, datatype=XSD.string)))

            g.add((customer_uri, EXT.hasEmail, email_uri))

        for device in customer["devices"]:
            device_uri = EXA[f"device_{device}"]

            g.add((device_uri, RDF.type, EXT.Device))
            g.add(
                (device_uri, EXT.identifierValue, Literal(device, datatype=XSD.string))
            )

            g.add((customer_uri, EXT.usesDevice, device_uri))

        for address in customer["addresses"]:
            address_uri = EXA[f"addr_{hashlib.sha1(address.encode()).hexdigest()[:10]}"]

            g.add((address_uri, RDF.type, EXT.PostalAddress))
            g.add(
                (
                    address_uri,
                    EXT.identifierValue,
                    Literal(address, datatype=XSD.string),
                )
            )

            g.add((customer_uri, EXT.livesAt, address_uri))

        for order in customer["orders"]:
            order_uri = EXA[f"order_{order['id']}"]

            g.add((order_uri, RDF.type, EXT.Order))
            g.add(
                (
                    order_uri,
                    EXT.amount,
                    Literal(str(order["amount"]), datatype=XSD.decimal),
                )
            )
            g.add(
                (order_uri, EXT.orderDate, Literal(order["orderDate"], datatype=XSD.date))
            )
            g.add((order_uri, EXT.placedBy, customer_uri))

            invoice = order["invoice"]
            invoice_uri = EXA[f"invoice_{invoice['id']}"]

            g.add((invoice_uri, RDF.type, EXT.Invoice))
            g.add((invoice_uri, EXT.invoiceFor, order_uri))
            g.add(
                (
                    invoice_uri,
                    EXT.paymentStatus,
                    Literal(invoice["paymentStatus"], datatype=XSD.string),
                )
            )
            g.add(
                (
                    invoice_uri,
                    EXT.dueDate,
                    Literal(invoice["dueDate"], datatype=XSD.date),
                )
            )

    return g


if __name__ == "__main__":
    with open("data/data.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
        customer_data = json_data["customers"]

        rdf_graph = create_rdf_from_json(customer_data)

        rdf_graph.serialize(destination="ontology/fraud_abox.ttl", format="turtle")
