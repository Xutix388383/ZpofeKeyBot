
-- ZpofeHub GUI Key Input System with Discord Bot Integration
-- This creates a GUI for users to enter their license keys

local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local API_BASE = "https://your-replit-url.replit.app" -- Replace with your actual Replit URL

-- Create the main GUI
local function createKeyInputGUI()
    -- Remove existing GUI if it exists
    if playerGui:FindFirstChild("ZpofeHubGUI") then
        playerGui.ZpofeHubGUI:Destroy()
    end
    
    -- Create ScreenGui
    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "ZpofeHubGUI"
    screenGui.ResetOnSpawn = false
    screenGui.Parent = playerGui
    
    -- Create main frame
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainFrame"
    mainFrame.Size = UDim2.new(0, 450, 0, 350)
    mainFrame.Position = UDim2.new(0.5, -225, 0.5, -175)
    mainFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 35)
    mainFrame.BorderSizePixel = 0
    mainFrame.Parent = screenGui
    
    -- Add corner radius
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 12)
    corner.Parent = mainFrame
    
    -- Add stroke
    local stroke = Instance.new("UIStroke")
    stroke.Color = Color3.fromRGB(100, 50, 200)
    stroke.Thickness = 2
    stroke.Parent = mainFrame
    
    -- Title
    local title = Instance.new("TextLabel")
    title.Name = "Title"
    title.Size = UDim2.new(1, 0, 0, 60)
    title.Position = UDim2.new(0, 0, 0, 0)
    title.BackgroundTransparency = 1
    title.Text = "🚀 ZpofeHub v2.0 - Discord Bot"
    title.TextColor3 = Color3.fromRGB(255, 255, 255)
    title.TextScaled = true
    title.Font = Enum.Font.GothamBold
    title.Parent = mainFrame
    
    -- Subtitle
    local subtitle = Instance.new("TextLabel")
    subtitle.Name = "Subtitle"
    subtitle.Size = UDim2.new(1, -20, 0, 30)
    subtitle.Position = UDim2.new(0, 10, 0, 55)
    subtitle.BackgroundTransparency = 1
    subtitle.Text = "Discord Bot Integration • Premium Script Protection"
    subtitle.TextColor3 = Color3.fromRGB(150, 150, 200)
    subtitle.TextScaled = true
    subtitle.Font = Enum.Font.Gotham
    subtitle.Parent = mainFrame
    
    -- Instructions
    local instructions = Instance.new("TextLabel")
    instructions.Name = "Instructions"
    instructions.Size = UDim2.new(1, -20, 0, 40)
    instructions.Position = UDim2.new(0, 10, 0, 90)
    instructions.BackgroundTransparency = 1
    instructions.Text = "Use /userpanel in Discord to get your license key:"
    instructions.TextColor3 = Color3.fromRGB(200, 200, 200)
    instructions.TextScaled = true
    instructions.Font = Enum.Font.Gotham
    instructions.Parent = mainFrame
    
    -- Key input textbox
    local keyInput = Instance.new("TextBox")
    keyInput.Name = "KeyInput"
    keyInput.Size = UDim2.new(1, -40, 0, 45)
    keyInput.Position = UDim2.new(0, 20, 0, 140)
    keyInput.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    keyInput.BorderSizePixel = 0
    keyInput.Text = ""
    keyInput.PlaceholderText = "ZPOFES-XXXXXXXXXXXX"
    keyInput.TextColor3 = Color3.fromRGB(255, 255, 255)
    keyInput.PlaceholderColor3 = Color3.fromRGB(120, 120, 120)
    keyInput.TextScaled = true
    keyInput.Font = Enum.Font.RobotoMono
    keyInput.Parent = mainFrame
    
    local keyInputCorner = Instance.new("UICorner")
    keyInputCorner.CornerRadius = UDim.new(0, 8)
    keyInputCorner.Parent = keyInput
    
    -- Verify button
    local verifyButton = Instance.new("TextButton")
    verifyButton.Name = "VerifyButton"
    verifyButton.Size = UDim2.new(0, 150, 0, 45)
    verifyButton.Position = UDim2.new(0.5, -75, 0, 200)
    verifyButton.BackgroundColor3 = Color3.fromRGB(100, 50, 200)
    verifyButton.BorderSizePixel = 0
    verifyButton.Text = "🔍 Verify Key"
    verifyButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    verifyButton.TextScaled = true
    verifyButton.Font = Enum.Font.GothamBold
    verifyButton.Parent = mainFrame
    
    local verifyButtonCorner = Instance.new("UICorner")
    verifyButtonCorner.CornerRadius = UDim.new(0, 8)
    verifyButtonCorner.Parent = verifyButton
    
    -- Discord button
    local discordButton = Instance.new("TextButton")
    discordButton.Name = "DiscordButton"
    discordButton.Size = UDim2.new(0, 180, 0, 35)
    discordButton.Position = UDim2.new(0.5, -90, 0, 255)
    discordButton.BackgroundColor3 = Color3.fromRGB(88, 101, 242)
    discordButton.BorderSizePixel = 0
    discordButton.Text = "📋 Copy Discord Command"
    discordButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    discordButton.TextScaled = true
    discordButton.Font = Enum.Font.Gotham
    discordButton.Parent = mainFrame
    
    local discordButtonCorner = Instance.new("UICorner")
    discordButtonCorner.CornerRadius = UDim.new(0, 6)
    discordButtonCorner.Parent = discordButton
    
    -- Status label
    local statusLabel = Instance.new("TextLabel")
    statusLabel.Name = "StatusLabel"
    statusLabel.Size = UDim2.new(1, -20, 0, 30)
    statusLabel.Position = UDim2.new(0, 10, 0, 300)
    statusLabel.BackgroundTransparency = 1
    statusLabel.Text = "🟡 Ready to verify..."
    statusLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
    statusLabel.TextScaled = true
    statusLabel.Font = Enum.Font.Gotham
    statusLabel.Parent = mainFrame
    
    -- Close button
    local closeButton = Instance.new("TextButton")
    closeButton.Name = "CloseButton"
    closeButton.Size = UDim2.new(0, 35, 0, 35)
    closeButton.Position = UDim2.new(1, -40, 0, 5)
    closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    closeButton.BorderSizePixel = 0
    closeButton.Text = "✕"
    closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    closeButton.TextScaled = true
    closeButton.Font = Enum.Font.GothamBold
    closeButton.Parent = mainFrame
    
    local closeButtonCorner = Instance.new("UICorner")
    closeButtonCorner.CornerRadius = UDim.new(0, 17)
    closeButtonCorner.Parent = closeButton
    
    -- Animation
    mainFrame.Size = UDim2.new(0, 0, 0, 0)
    local openTween = TweenService:Create(mainFrame, TweenInfo.new(0.5, Enum.EasingStyle.Back), {
        Size = UDim2.new(0, 450, 0, 350)
    })
    openTween:Play()
    
    -- Get HWID function
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
    
    -- Verify key function
    local function verifyKey(key, hwid)
        local success, response = pcall(function()
            local url = API_BASE .. "/verify?key=" .. key .. "&hwid=" .. hwid
            return HttpService:GetAsync(url)
        end)
        
        if not success then
            return false, "Failed to connect to Discord bot server"
        end
        
        local data = HttpService:JSONDecode(response)
        return data.success, data.message or "Unknown error"
    end
    
    -- Button events
    verifyButton.MouseButton1Click:Connect(function()
        local key = keyInput.Text:gsub("%s+", "") -- Remove whitespace
        
        if key == "" then
            statusLabel.Text = "❌ Please enter a license key"
            statusLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
            return
        end
        
        if not string.find(key, "ZPOFES%-") then
            statusLabel.Text = "❌ Invalid key format - must start with ZPOFES-"
            statusLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
            return
        end
        
        -- Show verifying status
        verifyButton.Text = "🔄 Verifying..."
        verifyButton.BackgroundColor3 = Color3.fromRGB(255, 165, 0)
        statusLabel.Text = "🔄 Verifying with Discord bot..."
        statusLabel.TextColor3 = Color3.fromRGB(255, 255, 100)
        
        -- Get HWID and verify
        local hwid = getHWID()
        local verified, message = verifyKey(key, hwid)
        
        if verified then
            statusLabel.Text = "✅ " .. message
            statusLabel.TextColor3 = Color3.fromRGB(100, 255, 100)
            verifyButton.Text = "✅ Verified"
            verifyButton.BackgroundColor3 = Color3.fromRGB(50, 200, 50)
            
            -- Wait a moment then close GUI and load script
            wait(2)
            screenGui:Destroy()
            
            -- Load your main script here
            loadMainScript(key, hwid)
        else
            statusLabel.Text = "❌ " .. message
            statusLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
            verifyButton.Text = "🔍 Verify Key"
            verifyButton.BackgroundColor3 = Color3.fromRGB(100, 50, 200)
        end
    end)
    
    discordButton.MouseButton1Click:Connect(function()
        pcall(function()
            setclipboard("/userpanel")
            statusLabel.Text = "📋 Copied '/userpanel' to clipboard!"
            statusLabel.TextColor3 = Color3.fromRGB(100, 255, 100)
        end)
    end)
    
    closeButton.MouseButton1Click:Connect(function()
        screenGui:Destroy()
    end)
    
    -- Auto-paste from clipboard if available
    spawn(function()
        wait(0.5)
        pcall(function()
            local clipboard = getclipboard and getclipboard() or ""
            if clipboard and string.find(clipboard, "ZPOFES%-") then
                keyInput.Text = clipboard
                statusLabel.Text = "📋 Key detected from clipboard"
                statusLabel.TextColor3 = Color3.fromRGB(100, 255, 100)
            end
        end)
    end)
end

-- Function to load main script after verification
function loadMainScript(key, hwid)
    print("🚀 Loading ZpofeHub v2.0 with verified key:", key)
    
    game:GetService("StarterGui"):SetCore("SendNotification", {
        Title = "🎉 ZpofeHub v2.0",
        Text = "Loading main script with Discord bot integration...",
        Duration = 5
    })
    
    -- Load the updated script from pastebin
    local success, error = pcall(function()
        loadstring(game:HttpGet("https://pastebin.com/raw/DmRu7yE0"))()
    end)
    
    if not success then
        game:GetService("StarterGui"):SetCore("SendNotification", {
            Title = "❌ Load Error",
            Text = "Failed to load script: " .. tostring(error),
            Duration = 10
        })
    end
end

-- Start the GUI
createKeyInputGUI()
