## A Sample flow to create in powerplatform ##

SAMPLE_FLOW = {
    "environment": "Default-32f814a9-68c8-4ca1-93aa-5594523476b3",
    "connectionName": "shared-gmail-444b9c37-a162-47e0-bbaf-7c2a-3fa7cbbd",
    "connectionApiId": "/providers/Microsoft.PowerApps/apis/shared_gmail",
    "flowDisplayName": "PWN",
    "flowDefinition": {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {"$connections": {"defaultValue": {}, "type": "Object"}, "$authentication": {"defaultValue": {}, "type": "SecureObject"}},
        "triggers": {
            "When_a_new_email_arrives": {
                "recurrence": {"frequency": "Minute", "interval": 1},
                "metadata": {"operationMetadataId": "f8fda515-f436-4f4d-811d-33a37c6ea879"},
                "type": "OpenApiConnection",
                "inputs": {
                    "host": {
                        "apiId": "/providers/Microsoft.PowerApps/apis/shared_gmail",
                        "connectionName": "shared_gmail",
                        "operationId": "OnNewEmail",
                    },
                    "parameters": {
                        "label": "INBOX",
                        "importance": "All",
                        "starred": "All",
                        "fetchOnlyWithAttachments": False,
                        "includeAttachments": False,
                    },
                    "authentication": "@parameters('$authentication')",
                },
            }
        },
        "actions": {
            "Send_email_(V2)_2": {
                "runAfter": {},
                "metadata": {"operationMetadataId": "16392aa1-6da8-42ca-a366-18d69194da73"},
                "type": "OpenApiConnection",
                "inputs": {
                    "host": {
                        "apiId": "/providers/Microsoft.PowerApps/apis/shared_gmail",
                        "connectionName": "shared_gmail",
                        "operationId": "SendEmailV2",
                    },
                    "parameters": {"emailMessage/To": "imkrissmith@gmail.com"},
                    "authentication": "@parameters('$authentication')",
                },
            }
        },
    },
    "flowState": "Stopped",
    "connectionReferences": [
        {"connectionName": "shared-gmail-444b9c37-a162-47e0-bbaf-7c2a-3fa7cbbd", "id": "/providers/Microsoft.PowerApps/apis/shared_gmail"}
    ],
}
