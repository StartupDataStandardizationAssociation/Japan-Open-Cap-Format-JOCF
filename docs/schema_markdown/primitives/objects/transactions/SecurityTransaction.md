# Primitive - Security Transaction

ID = `https://jocf.startupstandard.org/jocf/main/schema/primitives/objects/transactions/SecurityTransaction.schema.json`

## Description
特定の証券単位でのトランザクションに関する基底クラス

## Properties

| PropertyName | Type | Required | Description |
|-------------|------|----------|-------------|
| security_id | string | Yes | 証券を一意に特定するための識別子。Issuanceイベントで採番された後、証券の譲渡、解除、解約などのイベントで証券の特定のために利用されるもの。 |