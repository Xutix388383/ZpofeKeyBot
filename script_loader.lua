-- ZpofeHub Script Loader with Discord Bot Integration
-- This script connects to your Discord bot's key verification system

local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local API_BASE = "https://your-replit-url.replit.app" -- Replace with your actual Replit URL

-- Get hardware ID (HWID)
local function getHWID()
    local hwid = ""
    pcall(function()
        hwid = game:GetService("RbxAnalyticsService"):GetClientId()
    end)
    if hwid == "" then
        hwid = tostring(game.JobId)
    end
    return hwid
end

-- Show notification
local function showNotification(title, text, duration)
    game:GetService("StarterGui"):SetCore("SendNotification", {
        Title = title,
        Text = text,
        Duration = duration or 5
    })
end

-- Verify license key with the Discord bot's API
local function verifyKey(key, hwid)
    local success, response = pcall(function()
        local url = API_BASE .. "/verify?key=" .. key .. "&hwid=" .. hwid
        return HttpService:GetAsync(url)
    end)

    if not success then
        return false, "Failed to connect to verification server"
    end

    local data = HttpService:JSONDecode(response)
    return data.success, data.message or "Unknown error"
end

-- Load the main ZpofeHub script
local function loadMainScript()
    showNotification("🚀 ZpofeHub", "Loading main script...", 3)

    -- Load your updated script from pastebin
    local success, error = pcall(function()
        loadstring(game:HttpGet("https://pastebin.com/raw/DmRu7yE0"))()
    end)

    if success then
        showNotification("✅ ZpofeHub", "Script loaded successfully!", 5)
    else
        showNotification("❌ ZpofeHub", "Failed to load script: " .. tostring(error), 10)
    end
end

-- Main execution
showNotification("🚀 ZpofeHub", "Starting Discord bot integration...", 3)
loadMainScript()