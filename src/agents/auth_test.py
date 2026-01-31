from azure.identity import DefaultAzureCredential

cred = DefaultAzureCredential()
cred.get_token("https://management.azure.com/.default")

print("Azure auth working from Codespace")

# {
#   "appId": "417c9b0b-5939-40f3-a3d3-34684e19b8f0",
#   "displayName": "github-codespace-agent",
#   "password": "48i8Q~kOWeDA~nR0qwcuUg4ha25Q3b2ouyHHpbEu",
#   "tenant": "b6dbb308-0c08-4ea1-923e-c216b25d92a5"
# }

# {
#   "condition": null,
#   "conditionVersion": null,
#   "createdBy": null,
#   "createdOn": "2026-01-31T08:52:16.278911+00:00",
#   "delegatedManagedIdentityResourceId": null,
#   "description": null,
#   "id": "/subscriptions/3628c8cd-5bbe-4b0d-bcb4-2afa41fffbd1/providers/Microsoft.Authorization/roleAssignments/d42b703c-f499-45a4-a4b4-20f14803fd0c",
#   "name": "d42b703c-f499-45a4-a4b4-20f14803fd0c",
#   "principalId": "7dec1456-74be-4a72-8742-f7ed86405e2b",
#   "principalType": "ServicePrincipal",
#   "roleDefinitionId": "/subscriptions/3628c8cd-5bbe-4b0d-bcb4-2afa41fffbd1/providers/Microsoft.Authorization/roleDefinitions/64702f94-c441-49e6-a78b-ef80e0188fee",
#   "scope": "/subscriptions/3628c8cd-5bbe-4b0d-bcb4-2afa41fffbd1",
#   "type": "Microsoft.Authorization/roleAssignments",
#   "updatedBy": "4cbadacb-4e39-440c-96d7-f9b8a6c6ba24",
#   "updatedOn": "2026-01-31T08:52:16.462917+00:00"
# }