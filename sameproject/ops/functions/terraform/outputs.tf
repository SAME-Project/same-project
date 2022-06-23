output "app_name" {
  value = azurerm_linux_function_app.wa.name
}

output "host_name" {
  value = data.azurerm_function_app.wa_workaround.default_hostname
}

output "host_credentials" {
  value     = azurerm_linux_function_app.wa.site_credential
  sensitive = true
}

output "storage_connection_string" {
  value     = azurerm_storage_account.sa.primary_connection_string
  sensitive = true
}
