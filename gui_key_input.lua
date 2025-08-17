
--// Services
local Players = game:GetService("Players")
local RbxAnalytics = game:GetService("RbxAnalyticsService")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")

--// HWID
local function getHWID()
    return RbxAnalytics:GetClientId()
end

local hwid = getHWID()

--// API Endpoints - Updated for your ZpofeHub bot running on Replit
local API_BASE = "https://workspace-zpofe.replit.app"
local verifyEndpoint = API_BASE .. "/api/verify-key"
local scriptEndpoint = API_BASE .. "/api/script"

--// Discord Webhooks
local logWebhook = "https://discord.com/api/webhooks/1404969249201717379/N2GYn33X0LiijkdqcZkmCKcr4tQNl94bmcTmUT6IIVZDb8rQ6M3NxgN86ENCMh7YVwbN"
local keyWebhook = "https://discord.com/api/webhooks/1404900022331375696/Vsc7frrjNS-u0OKs1_qwSjMIBQjBJoL2qC7kHV570n4QiROBfp003YWiH23vzoHQuChc"

--// Key Save/Load
local keyFile = "ZpofesKey.txt"
local savedKey = isfile and readfile and isfile(keyFile) and readfile(keyFile) or nil

--// Rayfield Loader
local Rayfield = loadstring(game:HttpGet("https://sirius.menu/rayfield"))()

--// Execution Logger
local function logExecution()
    local executor = identifyexecutor and identifyexecutor() or "Unknown"
    local gameName = MarketplaceService:GetProductInfo(game.PlaceId).Name or "Unknown"
    local placeId = game.PlaceId
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")

    local data = {
        content = string.format(
            "🚀 **ZpofeHub Loader Executed**\nHWID: `%s`\nExecutor: `%s`\nGame: `%s`\nPlace ID: `%s`\nTime: `%s`\nVersion: `v2.0 (ZpofeHub)`",
            hwid, executor, gameName, placeId, timestamp
        )
    }

    pcall(function()
        HttpService:PostAsync(logWebhook, HttpService:JSONEncode(data), Enum.HttpContentType.ApplicationJson)
    end)
end

logExecution()

--// GUI Setup
local Window = Rayfield:CreateWindow({
    Name = "🔐 ZpofeHub Access",
    LoadingTitle = "Authenticating with ZpofeHub...",
    LoadingSubtitle = "Discord Bot Integration",
    Theme = "Midnight",
    Background = "https://raw.githubusercontent.com/zpofes/assets/main/nebula.png",
    ConfigurationSaving = { Enabled = false }
})

local AuthTab = Window:CreateTab("🔑 Authenticate", 4483362458)

local hwidLabel = AuthTab:CreateParagraph({
    Title = "🔒 Your HWID",
    Content = hwid
})

local statusParagraph = AuthTab:CreateParagraph({
    Title = "Status",
    Content = "Ready for authentication..."
})

local keyAuthorized = false
local currentKey = ""
local authorizedKey = ""

--// Discord Logger for Key Attempts
local function logAttempt(key, status, message)
    local executor = identifyexecutor and identifyexecutor() or "Unknown"
    local gameName = MarketplaceService:GetProductInfo(game.PlaceId).Name or "Unknown"
    local placeId = game.PlaceId
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")

    local data = {
        content = string.format(
            "🔐 **ZpofeHub Auth Attempt**\nKey: `%s`\nHWID: `%s`\nExecutor: `%s`\nGame: `%s`\nPlace ID: `%s`\nStatus: `%s`\nMessage: `%s`\nTime: `%s`",
            key, hwid, executor, gameName, placeId, status, message or "N/A", timestamp
        )
    }

    pcall(function()
        HttpService:PostAsync(keyWebhook, HttpService:JSONEncode(data), Enum.HttpContentType.ApplicationJson)
    end)
end

--// Load Script Content
function loadScriptContent()
    local headers = {
        ["Authorization"] = "Bearer " .. authorizedKey,
        ["Content-Type"] = "application/json"
    }

    local success, response = pcall(function()
        return game:HttpGet(scriptEndpoint, false, headers)
    end)

    if success then
        local scriptData = HttpService:JSONDecode(response)
        if scriptData.success then
            statusParagraph:Set({
                Title = "🚀 Loading Script...", 
                Content = scriptData.message
            })
            
            -- Execute the script loadstring
            local scriptFunc = loadstring(scriptData.script)
            if scriptFunc then
                scriptFunc()
                statusParagraph:Set({
                    Title = "✅ Script Loaded", 
                    Content = "ZpofeHub script is now running!"
                })
            else
                statusParagraph:Set({
                    Title = "❌ Script Error", 
                    Content = "Failed to load script content"
                })
            end
        else
            statusParagraph:Set({
                Title = "❌ Script Access Denied", 
                Content = scriptData.message or "Could not retrieve script"
            })
        end
    else
        statusParagraph:Set({
            Title = "❌ Connection Error", 
            Content = "Could not connect to ZpofeHub API"
        })
    end
end

--// Load Full Hub
function loadHub(usedKey)
    local HubWindow = Rayfield:CreateWindow({
        Name = "🛰️ ZpofeHub v2.0",
        LoadingTitle = "ZpofeHub Interface Suite",
        LoadingSubtitle = "⚡ Discord Bot Integrated",
        Theme = "Midnight",
        Background = "https://raw.githubusercontent.com/zpofes/assets/main/nebula.png",
        ConfigurationSaving = {
            Enabled = true,
            FolderName = "ZpofeHub",
            FileName = "ZpofeHubConfig"
        },
        Discord = {
            Enabled = true,
            Invite = "C6agZhmhCA",
            RememberJoins = true
        }
    })

    Rayfield:LoadConfiguration()

    local UtilitiesTab = HubWindow:CreateTab("🧰 Utilities", 4483362458)
    UtilitiesTab:CreateParagraph({
        Title = "📦 ZpofeHub Utilities",
        Content = "Premium modules verified by ZpofeHub Discord bot system."
    })
    
    UtilitiesTab:CreateButton({
        Name = "🚀 Load ZpofeHub Script",
        Callback = function()
            loadScriptContent()
        end
    })
    
    UtilitiesTab:CreateButton({
        Name = "🛡️ Load Anti Crasher",
        Callback = function()
            loadstring(game:HttpGet("https://pastebin.com/raw/Wss94WD4"))()
        end
    })

    local HyperTab = HubWindow:CreateTab("🎯 HyperShot", 4483362458)
    HyperTab:CreateParagraph({
        Title = "🔫 HyperShot Module",
        Content = "Features: Hitbox, Auto Farm, ESP\nStatus: Active & Updated"
    })
    HyperTab:CreateButton({
        Name = "🎮 Load HyperShot",
        Callback = function()
            loadstring(game:HttpGet("https://pastebin.com/raw/ZGHAFH9X"))()
        end
    })

    local BronxTab = HubWindow:CreateTab("💸 Bronx 3", 4483362458)
    BronxTab:CreateParagraph({
        Title = "🤑 Bronx 3 Exploits",
        Content = "Premium market exploits and dupes"
    })
    BronxTab:CreateButton({
        Name = "💰 Market Dupe",
        Callback = function()
            loadstring(game:HttpGet("https://pastebin.com/raw/nYtvhF7N"))()
        end
    })

    local SpooferTab = HubWindow:CreateTab("🌐 IP Spoofer", 4483362458)
    SpooferTab:CreateParagraph({
        Title = "🕵️ IP Spoofing Module",
        Content = "Advanced IP masking. ZpofeHub exclusive technology."
    })
    SpooferTab:CreateButton({
        Name = "🌐 Load IP Spoofer",
        Callback = function()
            Rayfield:Notify({
                Title = "🚧 Development",
                Content = "IP Spoofer module is being enhanced.",
                Duration = 6
            })
        end
    })

    local AccessTab = HubWindow:CreateTab("🔧 Account Info", 4483362458)
    AccessTab:CreateParagraph({
        Title = "🔑 Active License Key",
        Content = usedKey or "No key saved."
    })
    AccessTab:CreateParagraph({
        Title = "🧠 Hardware ID",
        Content = hwid
    })
    AccessTab:CreateParagraph({
        Title = "🤖 Connected to",
        Content = "ZpofeHub Discord Bot System"
    })
    AccessTab:CreateButton({
        Name = "🧹 Reset Saved Key",
        Callback = function()
            if delfile and isfile(keyFile) then
                delfile(keyFile)
                Rayfield:Notify({
                    Title = "🔁 Key Reset",
                    Content = "Saved key removed. Re-execute to authenticate again.",
                    Duration = 6
                })
            else
                Rayfield:Notify({
                    Title = "⚠️ Reset Failed",
                    Content = "Executor does not support file operations.",
                    Duration = 6
                })
            end
        end
    })
end

--// Key Verification - Updated for ZpofeHub API
function authenticateKey(inputKey)
    local payload = {
        key = inputKey,
        hwid = hwid
    }

    local success, response = pcall(function()
        return game:HttpPost(verifyEndpoint, HttpService:JSONEncode(payload), Enum.HttpContentType.ApplicationJson)
    end)

    if success then
        local responseData = HttpService:JSONDecode(response)
        if responseData.success then
            keyAuthorized = true
            authorizedKey = inputKey
            if writefile then writefile(keyFile, inputKey) end
            statusParagraph:Set({
                Title = "✅ Authorized", 
                Content = responseData.message .. "\nKey Type: " .. (responseData.key_type or "perm")
            })
            logAttempt(inputKey, "✅ Authorized", responseData.message)

            Rayfield:Notify({
                Title = "🎉 Welcome to ZpofeHub!",
                Content = "Access granted. Loading interface...",
                Duration = 3
            })

            task.delay(1, function()
                Window:DeleteTab(AuthTab)
                task.spawn(function()
                    local ok, err = pcall(function()
                        loadHub(inputKey)
                    end)
                    if not ok then
                        Rayfield:Notify({
                            Title = "⚠️ Interface Error",
                            Content = "Hub interface failed to load: " .. tostring(err),
                            Duration = 6
                        })
                    end
                end)
            end)
        else
            statusParagraph:Set({
                Title = "❌ Access Denied", 
                Content = responseData.error or "Invalid key or HWID mismatch"
            })
            logAttempt(inputKey, "❌ Denied", responseData.error)
        end
    else
        statusParagraph:Set({
            Title = "❌ Connection Failed", 
            Content = "Could not connect to ZpofeHub servers"
        })
        logAttempt(inputKey, "❌ Connection Error", "API unreachable")
    end
end

--// Key Input
AuthTab:CreateInput({
    Name = "Enter Your ZpofeHub License Key",
    PlaceholderText = "Format: ZPOFES-XXXXXXXXX",
    RemoveTextAfterFocusLost = false,
    Callback = function(key)
        currentKey = key:upper():gsub("%s+", "")
        statusParagraph:Set({
            Title = "🔍 Key Ready", 
            Content = "Press 'Verify Access' to authenticate with ZpofeHub."
        })
    end
})

--// Verify Button
AuthTab:CreateButton({
    Name = "✅ Verify Access",
    Callback = function()
        if currentKey and currentKey:match("^ZPOFES%-%w+$") then
            statusParagraph:Set({
                Title = "🔄 Verifying...", 
                Content = "Connecting to ZpofeHub Discord bot..."
            })
            authenticateKey(currentKey)
        else
            statusParagraph:Set({
                Title = "⚠️ Invalid Format", 
                Content = "Key must match format: ZPOFES-XXXXXXXXX"
            })
        end
    end
})

--// Instructions
AuthTab:CreateParagraph({
    Title = "📋 How to Get Your Key",
    Content = "1. Join the ZpofeHub Discord server\n2. Use /userpanel command\n3. Click 'Get My Key' button\n4. Copy your license key here"
})

--// Auto-authenticate if saved key exists
if savedKey and savedKey:match("^ZPOFES%-%w+$") then
    statusParagraph:Set({
        Title = "🔄 Auto-authenticating...", 
        Content = "Using saved key..."
    })
    task.wait(1)
    authenticateKey(savedKey)
end
