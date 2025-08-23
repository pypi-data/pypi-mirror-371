
## CATO-CLI - mutation.sites.addIpsecIkeV2SiteTunnels:
[Click here](https://api.catonetworks.com/documentation/#mutation-addIpsecIkeV2SiteTunnels) for documentation on this operation.

### Usage for mutation.sites.addIpsecIkeV2SiteTunnels:

`catocli mutation sites addIpsecIkeV2SiteTunnels -h`

`catocli mutation sites addIpsecIkeV2SiteTunnels <json>`

`catocli mutation sites addIpsecIkeV2SiteTunnels "$(cat < addIpsecIkeV2SiteTunnels.json)"`

`catocli mutation sites addIpsecIkeV2SiteTunnels '{"addIpsecIkeV2SiteTunnelsInput": {"addIpsecIkeV2TunnelsInput": {"destinationType": {"destinationType": "enum(DestinationType)"}, "popLocationId": {"popLocationId": "ID"}, "publicCatoIpId": {"publicCatoIpId": "ID"}, "tunnels": {"lastMileBw": {"downstream": {"downstream": "Int"}, "downstreamMbpsPrecision": {"downstreamMbpsPrecision": "Float"}, "upstream": {"upstream": "Int"}, "upstreamMbpsPrecision": {"upstreamMbpsPrecision": "Float"}}, "name": {"name": "String"}, "privateCatoIp": {"privateCatoIp": "IPAddress"}, "privateSiteIp": {"privateSiteIp": "IPAddress"}, "psk": {"psk": "String"}, "publicSiteIp": {"publicSiteIp": "IPAddress"}, "role": {"role": "enum(IPSecV2TunnelRole)"}}}}, "siteId": "ID"}'`

#### Operation Arguments for mutation.sites.addIpsecIkeV2SiteTunnels ####
`accountId` [ID] - (required) N/A 
`addIpsecIkeV2SiteTunnelsInput` [AddIpsecIkeV2SiteTunnelsInput] - (required) N/A 
`siteId` [ID] - (required) N/A 
