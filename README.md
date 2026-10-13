# Fraud detection with a knowledge graph

A learning project on graph-based fraud detection: ontology design (OWL/RDFS, built in
Protégé), synthetic data generation, and detection queries in SPARQL on GraphDB.


## Ontology

- **Classes:** `Customer` (sub-class `FraudulentCustomer`, sub-class `SuspiciousCustomer`),
  `Order`, `Invoice`, and `Identifier` with `Iban`, `PhoneNumber`, `EmailAddress`,
  `Device`, `PostalAddress`.
- **Properties:** `hasIban`, `hasPhone`, `hasEmail`, `usesDevice`, `livesAt` are
  sub-properties of `hasIdentifier`, so one query covers every identifier type.
  Inverses (`isIbanOf`, …) and a symmetric `sharesIdentifierWith`.
- **Disjointness:** `Customer`, `Order`, `Invoice`, `Identifier` are pairwise disjoint,
  as are the five identifier types.

## Queries

| File | Question | Needs inference |
|---|---|---|
| `01` | Customers sharing an IBAN | no |
| `02` | Identifiers used by more than one customer | RDFS (sub-properties) |
| `03` | Customers sharing a device with a confirmed fraudster | no |
| `04` | Overdue invoice and a shared identifier | RDFS |
| `05` | Customers linked, even indirectly, to a fraudster (property path) | RDFS |
| `06` | Customers per device | no |
| `10`–`13` | `INSERT`: distance 1 to 4 to the nearest fraudster | RDFS |
| `14` | Check of the computed distances | no |

## Tools

Protégé (HermiT), GraphDB Free, SPARQL 1.1, Python, `rdflib`.
