#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------#  
import bpy
from bpy.props import BoolProperty
from bpy.types import Panel
import urllib
from urllib import request
from urllib.request import urlopen
from html.parser import HTMLParser

#-----------------------------------------------------#  
#     handles crypto UI panel    
#-----------------------------------------------------#  
class DarrowCryptoPanel(bpy.types.Panel):
    bl_label = "Cryptocurrency"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_cryptoPanel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.crypto_moduleBool == True
            #print("poll")
 
    #def draw_header(self, context):
        # Example property to display a checkbox, can be anything
        #self.layout.prop(context.scene.render, "use_border", text="")
            
    def draw(self, context):
        crypto_module = bpy.types.BoolProperty
        Var_use_alerts = bpy.context.scene.usealertsBool
        Var_hidetools = bpy.context.scene.hidetoolkitBool

        layout = self.layout
        split=layout.split()
        col=split.column(align = True) 
        obj = context.scene
    
        box = layout.box()
        box.prop(context.scene, "btc_price")
        box.prop(context.scene, "eth_price")
        box.prop(context.scene, "xrp_price")

        box.prop(obj, 'autoupdateBool')
        split=box.split()
        split.operator('update.prices')
        split.operator('reset.prices')

        box = layout.box()
        box.prop(obj, "alertsinheaderBool")
    
        if bpy.context.scene.alertsinheaderBool == True:
            box.prop(obj, 'headerOptions')
            
        box = layout.box()
        box.prop(obj, "usealertsBool")
        
        if Var_use_alerts == True:
        
            split=box.split()
            split.label(text = "When prices are:")
            split.prop(obj, 'alertOptions')
            split=box.split()
            split.prop(obj, 'btcalertBool')
            split.prop(obj, 'ethalertBool')
            split.prop(obj, 'xrpalertBool')
            
            if bpy.context.scene.btcalertBool == True:
                box.prop(context.scene, "btc_alert")
            if bpy.context.scene.ethalertBool == True:   
                box.prop(context.scene, "eth_alert")
            if bpy.context.scene.xrpalertBool == True: 
                box.prop(context.scene, "xrp_alert")

#-----------------------------------------------------#  
#     Hanldes crypto notifcation Menu      
#-----------------------------------------------------#                   
class DarrowPriceMenu(bpy.types.Menu):
    bl_label = "Prices have moved!"
    bl_idname = "Darrow.PriceMenu"
    bl_idname = "DARROW_MT_priceMenu"
    
    def draw(self, context):
        layout = self.layout
        
        if bpy.context.scene.btcalertBool == True:
            layout.prop(context.scene, "btc_price")
        if bpy.context.scene.ethalertBool == True:
            layout.prop(context.scene, "eth_price")
        if bpy.context.scene.xrpalertBool == True:
            layout.prop(context.scene, "xrp_price")
        
        #bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)

#-----------------------------------------------------#  
#      Handles crypto prices displayed in header 
#-----------------------------------------------------#     
class DarrowHeaderPanel(bpy.types.Operator):
    bl_idname = "header.prices"
    bl_label = "BTC PRICE"
    bl_description = "This operator does something"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        print("Hello")
        bpy.ops.auto.update()
        return {"FINISHED"}

def draw(self, context):
    if bpy.context.scene.alertsinheaderBool == True:

        Var_header_options = bpy.context.scene.headerOptions
        
        layout = self.layout
        box = layout.box()
        box.operator('update.prices')
        
        if Var_header_options == 'OP1':
            #box = layout.box()
            box = layout.box()
            layout.prop(context.scene, "btc_price")     
            layout.prop(context.scene, "eth_price")
            layout.prop(context.scene, "xrp_price")
            
        if Var_header_options == 'OP2':
            box = layout.box()
            box.prop(context.scene, "btc_price")
            
        if Var_header_options == 'OP3':
            box = layout.box()
            box.prop(context.scene, "eth_price")
            
        if Var_header_options == 'OP4':
            box = layout.box()
            box.prop(context.scene, "xrp_price")

#-----------------------------------------------------#  
#     handles reseting of crypto prices     
#-----------------------------------------------------#   
class DarrowResetPrices(bpy.types.Operator):
    bl_idname = "reset.prices"
    bl_description = "Reset/restart all values"
    bl_label = "Reset"

    def execute(self, context):

        # resets url
        context.scene.btc_url = "null"
        context.scene.eth_url = "null"
        context.scene.xrp_url = "null"
        
        # print result
        print("url: Reset",context.scene.btc_url)
        print("url: Reset",context.scene.eth_url)
        print("url: Reset",context.scene.xrp_url)
        
        # resets price display
        context.scene.btc_price = "0.00"
        context.scene.eth_price = "0.00"
        context.scene.xrp_price = "0.00"
        
        # resets alerts
        context.scene.btc_alert = 25000
        context.scene.eth_alert = 500
        context.scene.xrp_alert = 0.35
        
        self.report({'INFO'}, "Prices Reset")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     handles fetching of prices from url  
#-----------------------------------------------------#  
class DarrowUpdatePrices(bpy.types.Operator):
    bl_idname = "update.prices"
    bl_description = "Check internet for prices"
    bl_label = "Check Update"
    
    def execute(self, context):
        btc_url = context.scene.btc_url
        eth_url = context.scene.eth_url
        xrp_url = context.scene.xrp_url
 
        #       Get bitcoin price from the internet    
        btc_url = 'https://coinmarketcap.com/'
        btc_response = urlopen(btc_url)
        #raw html code from url
        btc_rawstring = btc_response.read().decode('utf-8')
        #find these specific characters in the raw html. These are right before the price of bitcoin, so they are static
        btc_static = btc_rawstring.find('/currencies/bitcoin/markets/')
        #add a character buffer to get closer to price positions in raw string
        btc_buffer = 47
        #add the buffer to the static identifer to get the actual string start value for btc
        btc_startprice = btc_static + btc_buffer
        #add another buffer starting from the 'btc_startprice' to make sure we get the full price
        btc_endprice = btc_startprice + 10
        #get the actual price of btc by searching the raw string within these parameters
        btcprice = (btc_rawstring[btc_startprice:btc_endprice])
        #set global btc_price variable
        context.scene.btc_price = btcprice
        #     Get Etherum price from the internet    
        eth_url = 'https://coinmarketcap.com/'
        eth_response = urlopen(eth_url)
        #raw html code from url
        eth_rawstring = eth_response.read().decode('utf-8')
        #find these specific characters in the raw html. These are right before the price of bitcoin, so they are static
        eth_static = eth_rawstring.find('/currencies/ethereum/markets/')
        #add a character buffer to get closer to price positions in raw string
        eth_buffer = 48
        #add the buffer to the static identifer to get the actual string start value for btc
        eth_startprice = eth_static + eth_buffer
        #add another buffer starting from the 'btc_startprice' to make sure we get the full price
        eth_endprice = eth_startprice + 9
        #get the actual price of btc by searching the raw string within these parameters
        ethprice = (eth_rawstring[eth_startprice:eth_endprice])
        #set global btc_price variable
        context.scene.eth_price = ethprice
        #     Get Ripple price from the internet    
        xrp_url = 'https://coinmarketcap.com/'
        xrp_response = urlopen(xrp_url)
        #raw html code from url
        xrp_rawstring = xrp_response.read().decode('utf-8')
        #find these specific characters in the raw html. These are right before the price of bitcoin, so they are static
        xrp_static = xrp_rawstring.find('/currencies/xrp/markets/')
        #add a character buffer to get closer to price positions in raw string
        xrp_buffer = 43
        #add the buffer to the static identifer to get the actual string start value for btc
        xrp_startprice = xrp_static + xrp_buffer
        #add another buffer starting from the 'btc_startprice' to make sure we get the full price
        xrp_endprice = xrp_startprice + 7
        #get the actual price of btc by searching the raw string within these parameters
        xrpprice = (xrp_rawstring[xrp_startprice:xrp_endprice])
        #set global btc_price variable
        context.scene.xrp_price = xrpprice

        #-----------------------------------------------------#  
        #     Alerts
        #-----------------------------------------------------# 
        print("",)
        print("-----STRING VALUES-----",)
        print("BTC:",btcprice)
        print("ETH:",ethprice)
        print("XRP:",xrpprice)
        print("-----------------------",)
        print("",)   

        # BTC Alerts
        btc_alert = context.scene.btc_alert
        btc_alert = str(btc_alert)
        
        btc_str_bfprice = btcprice.replace("$", '')
        btc_str_price = btc_str_bfprice.replace(",", '')
        
        print("",)
        print("BITCOIN",)
        print("-----Price-----",)
        print(btc_str_price)
        print("-----Alert-----",)
        print(btc_alert)
        print("",)
        
        # ETH Alerts
        eth_alert = context.scene.eth_alert
        eth_alert = str(eth_alert)
        
        eth_str_bfprice = ethprice.replace("$", '')
        eth_str_price = eth_str_bfprice.replace(",", '')

        print("ETHEREUM",)
        print("-----Price-----",)
        print(eth_str_price)
        print("-----Alert-----",)
        print(eth_alert)
        print("",)
        
        # XRP Alerts 
        xrp_alert = context.scene.xrp_alert
        xrp_alert = float(xrp_alert)
        
        xrp_str_price = xrpprice.replace("$", '')
        xrp_str_price = float(xrp_str_price)
        
        print("RIPPLE",)
        print("-----Price-----",)
        print(xrp_str_price)
        print("-----Alert-----",)
        print(xrp_alert)
        print("",)

        Var_alert_options = bpy.context.scene.alertOptions
        Var_xrp = bpy.context.scene.xrpalertBool
        Var_eth = bpy.context.scene.ethalertBool
        Var_btc = bpy.context.scene.btcalertBool
    
        if bpy.context.scene.usealertsBool == True:

            if Var_alert_options == 'OP1':
               
                if Var_btc == True:     
                    if (btc_str_price >= btc_alert):
                        print("ALERT: BTC ABOVE")
                        bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
                        
                if Var_eth == True:
                    if (eth_str_price >= eth_alert):
                        print("ALERT: ETH ABOVE")
                        bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
                        
                if Var_xrp == True:
                    if (xrp_str_price >= xrp_alert):
                        print("ALERT: XRP ABOVE")
                        bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
                    
            if Var_alert_options == 'OP2':
        
                if Var_btc == True:
                    if (btc_str_price <= btc_alert):
                        print("ALERT: BTC BELOW")
                        bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
                if Var_eth == True:
                    if (eth_str_price <= eth_alert):
                        print("ALERT: ETH BELOW")
                        bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
                if Var_xrp == True:
                    if (xrp_str_price <= xrp_alert):
                        print("ALERT: XRP BELOW")
                        bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
                        
        #print("url:",btc_url)
        #print("url:",eth_url)
        #print("url:",xrp_url)
    
        self.report({'INFO'}, "Prices Refreshed")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Auto Update prices on interaction 
#-----------------------------------------------------#     
class DarrowAutoUpdate(bpy.types.Operator):
    bl_idname = "auto.update"
    bl_description = ""
    bl_label = ""

    def execute(self, context):
        if bpy.context.scene.autoupdateBool == True:
            bpy.ops.update.prices()

        self.report({'INFO'}, "Prices Refreshed")
        return {'FINISHED'}


#-----------------------------------------------------#  
#     Class registration 
#-----------------------------------------------------#    
classes = (DarrowCryptoPanel, DarrowPriceMenu, DarrowHeaderPanel, DarrowResetPrices, DarrowUpdatePrices, DarrowAutoUpdate)

def register():
    bpy.types.VIEW3D_HT_header.prepend(draw)
    for cls in classes:
        bpy.utils.register_class(cls)

    #-----------------------------------------------------#  
    #    Properties for crypto module 
    #-----------------------------------------------------#     

    bpy.types.Scene.btc_price = bpy.props.StringProperty(
    name = "BTC",
    description = "Current price of Bitcoin",
    )
    
    bpy.types.Scene.eth_price = bpy.props.StringProperty(
    name = "ETH",
    description = "Current price of Ethereum"
    )
    
    bpy.types.Scene.xrp_price = bpy.props.StringProperty(
    name = "XRP",
    description = "Current price of Ripple",
    )
    
    bpy.types.Scene.btc_url = bpy.props.StringProperty(
    name = "BTC URL",
    description = "",
    )
    
    bpy.types.Scene.eth_url = bpy.props.StringProperty(
    name = "ETH URL",
    description = "",
    )
    
    bpy.types.Scene.xrp_url = bpy.props.StringProperty(
    name = "xrp URL",
    description = "",
    )
    
    bpy.types.Scene.btc_alert = bpy.props.FloatProperty(
    name = "BTC:",
    )
    
    bpy.types.Scene.eth_alert = bpy.props.FloatProperty(
    name = "ETH:",
    )
    
    bpy.types.Scene.xrp_alert = bpy.props.FloatProperty(
    name = "XRP:",
    )

    bpy.types.Scene.alertsinheaderBool = bpy.props.BoolProperty(
    name = "Show prices in header",
    description = "Toggle visabilty of crypto prices in 3d viewport header",
    default = False
    )

    bpy.types.Scene.autoupdateBool = bpy.props.BoolProperty(
    name = "Auto Update",
    description = "Update crypto prices with interaction in toolkit items",
    default = False
    )
    
    bpy.types.Scene.usealertsBool = bpy.props.BoolProperty(
    name = "Alert me when",
    description = "Price alerts toggle",
    default = False
    )
    
    bpy.types.Scene.btcalertBool = bpy.props.BoolProperty(
    name = "BTC",
    description = "BTC Price alerts",
    default = False
    )
    
    bpy.types.Scene.ethalertBool = bpy.props.BoolProperty(
    name = "ETH",
    description = "ETH Price alerts",
    default = False
    )
    
    bpy.types.Scene.xrpalertBool = bpy.props.BoolProperty(
    name = "XRP",
    description = "XRP Price alerts",
    default = False
    )
    
    bpy.types.Scene.hidetoolkitBool = bpy.props.BoolProperty(
    name = "Crypto only",
    description = "Hide additional tools",
    default = False
    )

    bpy.types.Scene.alertOptions = bpy.props.EnumProperty(
    name="",
    description="If price is:.",
    items=[('OP1', "Greater than:", ""),
           ('OP2', "Less than:", ""),
        ]
    )
    
    bpy.types.Scene.headerOptions = bpy.props.EnumProperty(
    name="",
    description="If price is:.",
    default='OP2',
    items=[('OP1', "Show All", ""),
           ('OP2', "Only BTC", ""),
           ('OP3', "Only ETH", ""),
           ('OP4', "Only XRP", ""),
        ]
    )

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()