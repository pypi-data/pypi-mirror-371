
## CATO-CLI - mutation.sites.updateSocketInterface:
[Click here](https://api.catonetworks.com/documentation/#mutation-updateSocketInterface) for documentation on this operation.

### Usage for mutation.sites.updateSocketInterface:

`catocli mutation sites updateSocketInterface -h`

`catocli mutation sites updateSocketInterface <json>`

`catocli mutation sites updateSocketInterface "$(cat < updateSocketInterface.json)"`

`catocli mutation sites updateSocketInterface '{"siteId": "ID", "socketInterfaceId": "enum(SocketInterfaceIDEnum)", "updateSocketInterfaceInput": {"destType": {"destType": "enum(SocketInterfaceDestType)"}, "name": {"name": "String"}, "socketInterfaceAltWanInput": {"privateGatewayIp": {"privateGatewayIp": "IPAddress"}, "privateInterfaceIp": {"privateInterfaceIp": "IPAddress"}, "privateNetwork": {"privateNetwork": "IPSubnet"}, "privateVlanTag": {"privateVlanTag": "Int"}, "publicGatewayIp": {"publicGatewayIp": "IPAddress"}, "publicInterfaceIp": {"publicInterfaceIp": "IPAddress"}, "publicNetwork": {"publicNetwork": "IPSubnet"}, "publicVlanTag": {"publicVlanTag": "Int"}}, "socketInterfaceBandwidthInput": {"downstreamBandwidth": {"downstreamBandwidth": "Int"}, "downstreamBandwidthMbpsPrecision": {"downstreamBandwidthMbpsPrecision": "Float"}, "upstreamBandwidth": {"upstreamBandwidth": "Int"}, "upstreamBandwidthMbpsPrecision": {"upstreamBandwidthMbpsPrecision": "Float"}}, "socketInterfaceLagInput": {"minLinks": {"minLinks": "Int"}}, "socketInterfaceLanInput": {"localIp": {"localIp": "IPAddress"}, "subnet": {"subnet": "IPSubnet"}, "translatedSubnet": {"translatedSubnet": "IPSubnet"}}, "socketInterfaceOffCloudInput": {"enabled": {"enabled": "Boolean"}, "publicIp": {"publicIp": "IPAddress"}, "publicStaticPort": {"publicStaticPort": "Int"}}, "socketInterfaceVrrpInput": {"vrrpType": {"vrrpType": "enum(VrrpType)"}}, "socketInterfaceWanInput": {"precedence": {"precedence": "enum(SocketInterfacePrecedenceEnum)"}, "role": {"role": "enum(SocketInterfaceRole)"}}}}'`

#### Operation Arguments for mutation.sites.updateSocketInterface ####
`accountId` [ID] - (required) N/A 
`siteId` [ID] - (required) N/A 
`socketInterfaceId` [SocketInterfaceIDEnum] - (required) N/A Default Value: ['LAN1', 'LAN2', 'WAN1', 'WAN2', 'USB1', 'USB2', 'INT_1', 'INT_2', 'INT_3', 'INT_4', 'INT_5', 'INT_6', 'INT_7', 'INT_8', 'INT_9', 'INT_10', 'INT_11', 'INT_12', 'WLAN', 'LTE']
`updateSocketInterfaceInput` [UpdateSocketInterfaceInput] - (required) N/A 
