terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.10.0"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {
    resource_group {
      # TODO: remove after this is working
      prevent_deletion_if_contains_resources = false
    }
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "same-resource-group"
  location = "West US"
}

resource "azurerm_storage_account" "sa" {
  name                     = "samestorageaccount"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_application_insights" "ai" {
  name                = "same-app-insights"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  application_type    = "web"
}

resource "azurerm_service_plan" "sp" {
  name                = "same-app-service-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku_name            = "Y1"
  os_type             = "Linux"
}

resource "azurerm_linux_function_app" "wa" {
  name                        = "same-site"
  resource_group_name         = azurerm_resource_group.rg.name
  location                    = azurerm_resource_group.rg.location
  service_plan_id             = azurerm_service_plan.sp.id
  storage_account_name        = azurerm_storage_account.sa.name
  functions_extension_version = "~4"

  app_settings = {
    "AzureWebJobsStorage" = azurerm_storage_account.sa.primary_connection_string
  }

  site_config {
    application_insights_connection_string = azurerm_application_insights.ai.connection_string
    application_insights_key               = azurerm_application_insights.ai.instrumentation_key

    application_stack {
      python_version = "3.8"
    }
  }
}

# Workaround to obtain the host URL, see the following github issue:
# https://github.com/hashicorp/terraform-provider-azurerm/issues/16263
data "azurerm_function_app" "wa_workaround" {
  name                = azurerm_linux_function_app.wa.name
  resource_group_name = azurerm_resource_group.rg.name
}
