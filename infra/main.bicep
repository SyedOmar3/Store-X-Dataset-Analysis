param location string = resourceGroup().location
param appName string = 'mortgage-${uniqueString(resourceGroup().id)}'

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${appName}-plan'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
}

resource apiApp 'Microsoft.Web/sites@2023-12-01' = {
  name: '${appName}-api'
  location: location
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appSettings: [
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
      ]
    }
  }
  kind: 'app,linux'
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: '${appName}-web'
  location: location
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
    }
  }
  kind: 'app,linux'
}

output apiUrl string = 'https://${apiApp.properties.defaultHostName}'
output webUrl string = 'https://${webApp.properties.defaultHostName}'
