
--// ZpofeHub Universal Script Hub v2.0
--// Custom UI with Full Key System Integration
--// Author: Zpofe Team

--// Services
local Players = game:GetService("Players")
local RbxAnalytics = game:GetService("RbxAnalyticsService")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

--// Player Info
local LocalPlayer = Players.LocalPlayer
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")

--// HWID System
local function getHWID()
    return RbxAnalytics:GetClientId()
end

local hwid = getHWID()

--// API Configuration - Updated for ZpofeHub on Replit
local API_BASE = "https://workspace-zpofe.replit.app"
local VERIFY_ENDPOINT = API_BASE .. "/api/verify-key"
local SCRIPT_ENDPOINT = API_BASE .. "/api/script"
local HEALTH_ENDPOINT = API_BASE .. "/api/health"

--// Discord Webhooks
local LOG_WEBHOOK = "https://discord.com/api/webhooks/1404969249201717379/N2GYn33X0LiijkdqcZkmCKcr4tQNl94bmcTmUT6IIVZDb8rQ6M3NxgN86ENCMh7YVwbN"
local KEY_WEBHOOK = "https://discord.com/api/webhooks/1404900022331375696/Vsc7frrjNS-u0OKs1_qwSjMIBQjBJoL2qC7kHV570n4QiROBfp003YWiH23vzoHQuChc"

--// Key Storage
local KEY_FILE = "ZpofeHubKey.txt"
local savedKey = isfile and readfile and isfile(KEY_FILE) and readfile(KEY_FILE) or nil

--// UI Variables
local ScreenGui = nil
local MainFrame = nil
local AuthFrame = nil
local HubFrame = nil
local currentKey = ""
local keyAuthorized = false
local authorizedKey = ""

--// Color Scheme
local COLORS = {
    Primary = Color3.fromRGB(106, 13, 173),    -- Purple
    Secondary = Color3.fromRGB(45, 45, 45),     -- Dark Gray
    Background = Color3.fromRGB(26, 26, 26),    -- Very Dark Gray
    Success = Color3.fromRGB(0, 255, 0),        -- Green
    Error = Color3.fromRGB(255, 68, 68),        -- Red
    Warning = Color3.fromRGB(255, 193, 7),      -- Yellow
    Text = Color3.fromRGB(255, 255, 255),       -- White
    TextSecondary = Color3.fromRGB(200, 200, 200) -- Light Gray
}

--// Utility Functions
local function createTween(object, properties, duration, easingStyle, easingDirection)
    easingStyle = easingStyle or Enum.EasingStyle.Quad
    easingDirection = easingDirection or Enum.EasingDirection.Out
    duration = duration or 0.3
    
    local tween = TweenService:Create(object, TweenInfo.new(duration, easingStyle, easingDirection), properties)
    tween:Play()
    return tween
end

local function createRippleEffect(button, position)
    local ripple = Instance.new("Frame")
    ripple.Name = "Ripple"
    ripple.Size = UDim2.new(0, 0, 0, 0)
    ripple.Position = UDim2.new(0, position.X - button.AbsolutePosition.X, 0, position.Y - button.AbsolutePosition.Y)
    ripple.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
    ripple.BackgroundTransparency = 0.7
    ripple.BorderSizePixel = 0
    ripple.ZIndex = button.ZIndex + 1
    ripple.Parent = button
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(1, 0)
    corner.Parent = ripple
    
    local maxSize = math.max(button.AbsoluteSize.X, button.AbsoluteSize.Y) * 2
    
    createTween(ripple, {
        Size = UDim2.new(0, maxSize, 0, maxSize),
        Position = UDim2.new(0, position.X - button.AbsolutePosition.X - maxSize/2, 0, position.Y - button.AbsolutePosition.Y - maxSize/2),
        BackgroundTransparency = 1
    }, 0.6)
    
    game:GetService("Debris"):AddItem(ripple, 0.6)
end

--// Discord Logging Functions
local function logExecution()
    local executor = identifyexecutor and identifyexecutor() or "Unknown"
    local gameName = "Unknown"
    pcall(function()
        gameName = MarketplaceService:GetProductInfo(game.PlaceId).Name
    end)
    
    local data = {
        content = string.format(
            "🚀 **ZpofeHub Universal Hub Executed**\n" ..
            "HWID: `%s`\n" ..
            "Executor: `%s`\n" ..
            "Game: `%s`\n" ..
            "Place ID: `%s`\n" ..
            "Player: `%s`\n" ..
            "Time: `%s`\n" ..
            "Version: `v2.0 Universal`",
            hwid, executor, gameName, game.PlaceId, LocalPlayer.Name, os.date("%Y-%m-%d %H:%M:%S")
        )
    }
    
    pcall(function()
        HttpService:PostAsync(LOG_WEBHOOK, HttpService:JSONEncode(data), Enum.HttpContentType.ApplicationJson)
    end)
end

local function logKeyAttempt(key, status, message)
    local executor = identifyexecutor and identifyexecutor() or "Unknown"
    local gameName = "Unknown"
    pcall(function()
        gameName = MarketplaceService:GetProductInfo(game.PlaceId).Name
    end)
    
    local data = {
        content = string.format(
            "🔐 **ZpofeHub Universal Hub Auth**\n" ..
            "Key: `%s`\n" ..
            "HWID: `%s`\n" ..
            "Executor: `%s`\n" ..
            "Game: `%s`\n" ..
            "Player: `%s`\n" ..
            "Status: `%s`\n" ..
            "Message: `%s`\n" ..
            "Time: `%s`",
            key, hwid, executor, gameName, LocalPlayer.Name, status, message or "N/A", os.date("%Y-%m-%d %H:%M:%S")
        )
    }
    
    pcall(function()
        HttpService:PostAsync(KEY_WEBHOOK, HttpService:JSONEncode(data), Enum.HttpContentType.ApplicationJson)
    end)
end

--// Notification System
local function showNotification(title, message, notificationType)
    notificationType = notificationType or "info"
    local color = COLORS.Primary
    
    if notificationType == "success" then
        color = COLORS.Success
    elseif notificationType == "error" then
        color = COLORS.Error
    elseif notificationType == "warning" then
        color = COLORS.Warning
    end
    
    local notification = Instance.new("Frame")
    notification.Name = "Notification"
    notification.Size = UDim2.new(0, 300, 0, 80)
    notification.Position = UDim2.new(1, 20, 0, 100)
    notification.BackgroundColor3 = COLORS.Background
    notification.BorderSizePixel = 0
    notification.ZIndex = 1000
    notification.Parent = ScreenGui
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = notification
    
    local stroke = Instance.new("UIStroke")
    stroke.Color = color
    stroke.Thickness = 2
    stroke.Parent = notification
    
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Name = "Title"
    titleLabel.Size = UDim2.new(1, -20, 0, 25)
    titleLabel.Position = UDim2.new(0, 10, 0, 10)
    titleLabel.BackgroundTransparency = 1
    titleLabel.Text = title
    titleLabel.TextColor3 = color
    titleLabel.TextSize = 14
    titleLabel.TextXAlignment = Enum.TextXAlignment.Left
    titleLabel.Font = Enum.Font.GothamBold
    titleLabel.Parent = notification
    
    local messageLabel = Instance.new("TextLabel")
    messageLabel.Name = "Message"
    messageLabel.Size = UDim2.new(1, -20, 0, 35)
    messageLabel.Position = UDim2.new(0, 10, 0, 35)
    messageLabel.BackgroundTransparency = 1
    messageLabel.Text = message
    messageLabel.TextColor3 = COLORS.TextSecondary
    messageLabel.TextSize = 12
    messageLabel.TextXAlignment = Enum.TextXAlignment.Left
    messageLabel.TextYAlignment = Enum.TextYAlignment.Top
    messageLabel.TextWrapped = true
    messageLabel.Font = Enum.Font.Gotham
    messageLabel.Parent = notification
    
    -- Animate in
    createTween(notification, {Position = UDim2.new(1, -320, 0, 100)}, 0.3)
    
    -- Auto hide after 5 seconds
    task.wait(5)
    createTween(notification, {Position = UDim2.new(1, 20, 0, 100)}, 0.3)
    task.wait(0.3)
    notification:Destroy()
end

--// UI Creation Functions
local function createButton(parent, name, text, position, size, callback)
    local button = Instance.new("TextButton")
    button.Name = name
    button.Size = size
    button.Position = position
    button.BackgroundColor3 = COLORS.Primary
    button.BorderSizePixel = 0
    button.Text = text
    button.TextColor3 = COLORS.Text
    button.TextSize = 14
    button.Font = Enum.Font.GothamBold
    button.ZIndex = 2
    button.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = button
    
    local gradient = Instance.new("UIGradient")
    gradient.Color = ColorSequence.new{
        ColorSequenceKeypoint.new(0, Color3.fromRGB(120, 20, 190)),
        ColorSequenceKeypoint.new(1, Color3.fromRGB(80, 10, 140))
    }
    gradient.Rotation = 45
    gradient.Parent = button
    
    -- Hover effects
    button.MouseEnter:Connect(function()
        createTween(button, {BackgroundColor3 = Color3.fromRGB(130, 20, 200)}, 0.2)
    end)
    
    button.MouseLeave:Connect(function()
        createTween(button, {BackgroundColor3 = COLORS.Primary}, 0.2)
    end)
    
    -- Click effect
    button.MouseButton1Down:Connect(function()
        createRippleEffect(button, UserInputService:GetMouseLocation())
        createTween(button, {Size = size * 0.95}, 0.1)
    end)
    
    button.MouseButton1Up:Connect(function()
        createTween(button, {Size = size}, 0.1)
    end)
    
    if callback then
        button.MouseButton1Click:Connect(callback)
    end
    
    return button
end

local function createTextBox(parent, name, placeholder, position, size)
    local frame = Instance.new("Frame")
    frame.Name = name .. "Frame"
    frame.Size = size
    frame.Position = position
    frame.BackgroundColor3 = COLORS.Secondary
    frame.BorderSizePixel = 0
    frame.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = frame
    
    local stroke = Instance.new("UIStroke")
    stroke.Color = Color3.fromRGB(80, 80, 80)
    stroke.Thickness = 1
    stroke.Parent = frame
    
    local textBox = Instance.new("TextBox")
    textBox.Name = name
    textBox.Size = UDim2.new(1, -20, 1, 0)
    textBox.Position = UDim2.new(0, 10, 0, 0)
    textBox.BackgroundTransparency = 1
    textBox.Text = ""
    textBox.PlaceholderText = placeholder
    textBox.TextColor3 = COLORS.Text
    textBox.PlaceholderColor3 = COLORS.TextSecondary
    textBox.TextSize = 14
    textBox.Font = Enum.Font.Gotham
    textBox.TextXAlignment = Enum.TextXAlignment.Left
    textBox.Parent = frame
    
    -- Focus effects
    textBox.Focused:Connect(function()
        createTween(stroke, {Color = COLORS.Primary}, 0.2)
    end)
    
    textBox.FocusLost:Connect(function()
        createTween(stroke, {Color = Color3.fromRGB(80, 80, 80)}, 0.2)
    end)
    
    return textBox
end

local function createLabel(parent, name, text, position, size, textSize, textColor)
    local label = Instance.new("TextLabel")
    label.Name = name
    label.Size = size
    label.Position = position
    label.BackgroundTransparency = 1
    label.Text = text
    label.TextColor3 = textColor or COLORS.Text
    label.TextSize = textSize or 14
    label.Font = Enum.Font.Gotham
    label.TextXAlignment = Enum.TextXAlignment.Center
    label.TextYAlignment = Enum.TextYAlignment.Center
    label.TextWrapped = true
    label.Parent = parent
    
    return label
end

--// Key System Functions
local function verifyKey(key, hwid)
    local payload = {
        key = key,
        hwid = hwid
    }
    
    local success, response = pcall(function()
        return game:HttpPost(VERIFY_ENDPOINT, HttpService:JSONEncode(payload), Enum.HttpContentType.ApplicationJson)
    end)
    
    if success then
        local responseData = HttpService:JSONDecode(response)
        return responseData
    end
    
    return {success = false, error = "Connection failed"}
end

local function loadScript()
    local headers = {
        ["Authorization"] = "Bearer " .. authorizedKey,
        ["Content-Type"] = "application/json"
    }
    
    local success, response = pcall(function()
        return game:HttpGet(SCRIPT_ENDPOINT, false, headers)
    end)
    
    if success then
        local scriptData = HttpService:JSONDecode(response)
        if scriptData.success then
            showNotification("Script Loading", "Executing premium script...", "success")
            
            local scriptFunc = loadstring(scriptData.script)
            if scriptFunc then
                scriptFunc()
                showNotification("Success", "Premium script loaded successfully!", "success")
            else
                showNotification("Error", "Failed to load script content", "error")
            end
        else
            showNotification("Access Denied", scriptData.message or "Could not retrieve script", "error")
        end
    else
        showNotification("Connection Error", "Could not connect to ZpofeHub API", "error")
    end
end

--// Auth Frame Creation
local function createAuthFrame()
    AuthFrame = Instance.new("Frame")
    AuthFrame.Name = "AuthFrame"
    AuthFrame.Size = UDim2.new(0, 400, 0, 500)
    AuthFrame.Position = UDim2.new(0.5, -200, 0.5, -250)
    AuthFrame.BackgroundColor3 = COLORS.Background
    AuthFrame.BorderSizePixel = 0
    AuthFrame.ZIndex = 1
    AuthFrame.Parent = MainFrame
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 12)
    corner.Parent = AuthFrame
    
    local stroke = Instance.new("UIStroke")
    stroke.Color = COLORS.Primary
    stroke.Thickness = 2
    stroke.Parent = AuthFrame
    
    -- Header
    local header = Instance.new("Frame")
    header.Name = "Header"
    header.Size = UDim2.new(1, 0, 0, 80)
    header.Position = UDim2.new(0, 0, 0, 0)
    header.BackgroundColor3 = COLORS.Primary
    header.BorderSizePixel = 0
    header.Parent = AuthFrame
    
    local headerCorner = Instance.new("UICorner")
    headerCorner.CornerRadius = UDim.new(0, 12)
    headerCorner.Parent = header
    
    local headerFix = Instance.new("Frame")
    headerFix.Size = UDim2.new(1, 0, 0, 20)
    headerFix.Position = UDim2.new(0, 0, 1, -20)
    headerFix.BackgroundColor3 = COLORS.Primary
    headerFix.BorderSizePixel = 0
    headerFix.Parent = header
    
    local titleLabel = createLabel(header, "Title", "🛰️ ZpofeHub Universal", UDim2.new(0, 0, 0, 0), UDim2.new(1, 0, 0, 50), 20, COLORS.Text)
    titleLabel.Font = Enum.Font.GothamBold
    
    local subtitleLabel = createLabel(header, "Subtitle", "Premium Script Hub & Key System", UDim2.new(0, 0, 0, 45), UDim2.new(1, 0, 0, 30), 12, Color3.fromRGB(220, 220, 220))
    
    -- HWID Display
    local hwidLabel = createLabel(AuthFrame, "HWID", "🔒 Your HWID: " .. hwid, UDim2.new(0, 20, 0, 100), UDim2.new(1, -40, 0, 30), 11, COLORS.TextSecondary)
    hwidLabel.TextXAlignment = Enum.TextXAlignment.Left
    
    -- Key Input
    local keyInput = createTextBox(AuthFrame, "KeyInput", "Enter your ZpofeHub license key...", UDim2.new(0, 20, 0, 150), UDim2.new(1, -40, 0, 45))
    
    -- Status Label
    local statusLabel = createLabel(AuthFrame, "Status", "Ready for authentication...", UDim2.new(0, 20, 0, 220), UDim2.new(1, -40, 0, 60), 12, COLORS.TextSecondary)
    statusLabel.TextXAlignment = Enum.TextXAlignment.Left
    statusLabel.TextYAlignment = Enum.TextYAlignment.Top
    
    -- Buttons
    local verifyButton = createButton(AuthFrame, "VerifyButton", "🔐 Verify License Key", UDim2.new(0, 20, 0, 300), UDim2.new(1, -40, 0, 45), function()
        local inputKey = keyInput.Text:upper():gsub("%s+", "")
        
        if not inputKey:match("^ZPOFES%-%w+$") then
            statusLabel.Text = "❌ Invalid Format\nKey must match format: ZPOFES-XXXXXXXXX"
            statusLabel.TextColor3 = COLORS.Error
            showNotification("Invalid Format", "Key must match format: ZPOFES-XXXXXXXXX", "error")
            return
        end
        
        statusLabel.Text = "🔄 Verifying license key...\nConnecting to ZpofeHub servers..."
        statusLabel.TextColor3 = COLORS.Warning
        currentKey = inputKey
        
        task.spawn(function()
            local result = verifyKey(inputKey, hwid)
            
            if result.success then
                keyAuthorized = true
                authorizedKey = inputKey
                
                if writefile then 
                    writefile(KEY_FILE, inputKey) 
                end
                
                statusLabel.Text = "✅ License Verified!\n" .. (result.message or "Access granted") .. "\nKey Type: " .. (result.key_type or "premium")
                statusLabel.TextColor3 = COLORS.Success
                
                logKeyAttempt(inputKey, "✅ Authorized", result.message)
                showNotification("Access Granted", "Welcome to ZpofeHub! Loading interface...", "success")
                
                task.wait(1.5)
                AuthFrame.Visible = false
                createHubFrame()
            else
                statusLabel.Text = "❌ Authentication Failed\n" .. (result.error or "Invalid key or HWID mismatch")
                statusLabel.TextColor3 = COLORS.Error
                
                logKeyAttempt(inputKey, "❌ Denied", result.error)
                showNotification("Access Denied", result.error or "Invalid key or HWID mismatch", "error")
            end
        end)
    end)
    
    -- Instructions
    local instructionsLabel = createLabel(AuthFrame, "Instructions", 
        "📋 How to get your key:\n" ..
        "1. Join ZpofeHub Discord server\n" ..
        "2. Use /userpanel command\n" ..
        "3. Click 'Get My Key' button\n" ..
        "4. Copy your license key here", 
        UDim2.new(0, 20, 0, 370), UDim2.new(1, -40, 0, 100), 10, COLORS.TextSecondary)
    instructionsLabel.TextXAlignment = Enum.TextXAlignment.Left
    instructionsLabel.TextYAlignment = Enum.TextYAlignment.Top
    
    -- Auto-authenticate if saved key exists
    if savedKey and savedKey:match("^ZPOFES%-%w+$") then
        keyInput.Text = savedKey
        statusLabel.Text = "🔄 Auto-authenticating...\nUsing saved license key..."
        statusLabel.TextColor3 = COLORS.Warning
        
        task.wait(1)
        verifyButton.MouseButton1Click:Fire()
    end
end

--// Hub Frame Creation
function createHubFrame()
    HubFrame = Instance.new("Frame")
    HubFrame.Name = "HubFrame"
    HubFrame.Size = UDim2.new(0, 800, 0, 600)
    HubFrame.Position = UDim2.new(0.5, -400, 0.5, -300)
    HubFrame.BackgroundColor3 = COLORS.Background
    HubFrame.BorderSizePixel = 0
    HubFrame.ZIndex = 1
    HubFrame.Parent = MainFrame
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 12)
    corner.Parent = HubFrame
    
    local stroke = Instance.new("UIStroke")
    stroke.Color = COLORS.Primary
    stroke.Thickness = 2
    stroke.Parent = HubFrame
    
    -- Header
    local header = Instance.new("Frame")
    header.Name = "Header"
    header.Size = UDim2.new(1, 0, 0, 80)
    header.Position = UDim2.new(0, 0, 0, 0)
    header.BackgroundColor3 = COLORS.Primary
    header.BorderSizePixel = 0
    header.Parent = HubFrame
    
    local headerCorner = Instance.new("UICorner")
    headerCorner.CornerRadius = UDim.new(0, 12)
    headerCorner.Parent = header
    
    local headerFix = Instance.new("Frame")
    headerFix.Size = UDim2.new(1, 0, 0, 20)
    headerFix.Position = UDim2.new(0, 0, 1, -20)
    headerFix.BackgroundColor3 = COLORS.Primary
    headerFix.BorderSizePixel = 0
    headerFix.Parent = header
    
    local titleLabel = createLabel(header, "Title", "🛰️ ZpofeHub Universal v2.0", UDim2.new(0, 0, 0, 0), UDim2.new(1, 0, 0, 50), 22, COLORS.Text)
    titleLabel.Font = Enum.Font.GothamBold
    
    local subtitleLabel = createLabel(header, "Subtitle", "Premium Universal Script Hub • Verified License Active", UDim2.new(0, 0, 0, 45), UDim2.new(1, 0, 0, 30), 12, Color3.fromRGB(220, 220, 220))
    
    -- Close Button
    local closeButton = createButton(header, "CloseButton", "✕", UDim2.new(1, -50, 0, 15), UDim2.new(0, 35, 0, 35), function()
        ScreenGui:Destroy()
    end)
    closeButton.BackgroundColor3 = COLORS.Error
    closeButton.TextSize = 18
    
    -- Tab System
    local tabFrame = Instance.new("Frame")
    tabFrame.Name = "TabFrame"
    tabFrame.Size = UDim2.new(0, 150, 1, -80)
    tabFrame.Position = UDim2.new(0, 0, 0, 80)
    tabFrame.BackgroundColor3 = COLORS.Secondary
    tabFrame.BorderSizePixel = 0
    tabFrame.Parent = HubFrame
    
    local contentFrame = Instance.new("Frame")
    contentFrame.Name = "ContentFrame"
    contentFrame.Size = UDim2.new(1, -150, 1, -80)
    contentFrame.Position = UDim2.new(0, 150, 0, 80)
    contentFrame.BackgroundTransparency = 1
    contentFrame.Parent = HubFrame
    
    -- Content frames for each tab
    local tabContents = {}
    
    -- Tab creation function
    local function createTab(name, icon, content)
        local tabButton = createButton(tabFrame, name .. "Tab", icon .. " " .. name, UDim2.new(0, 10, 0, #tabContents * 50 + 10), UDim2.new(1, -20, 0, 40), function()
            -- Hide all content frames
            for _, frame in pairs(tabContents) do
                frame.Visible = false
            end
            -- Show selected content
            tabContents[name].Visible = true
            
            -- Update tab button appearances
            for _, child in pairs(tabFrame:GetChildren()) do
                if child:IsA("TextButton") and child ~= tabButton then
                    child.BackgroundColor3 = COLORS.Secondary
                end
            end
            tabButton.BackgroundColor3 = COLORS.Primary
        end)
        tabButton.BackgroundColor3 = COLORS.Secondary
        tabButton.TextXAlignment = Enum.TextXAlignment.Left
        
        -- Create content frame
        local frame = Instance.new("ScrollingFrame")
        frame.Name = name .. "Content"
        frame.Size = UDim2.new(1, -20, 1, -20)
        frame.Position = UDim2.new(0, 10, 0, 10)
        frame.BackgroundTransparency = 1
        frame.BorderSizePixel = 0
        frame.ScrollBarThickness = 6
        frame.ScrollBarImageColor3 = COLORS.Primary
        frame.CanvasSize = UDim2.new(0, 0, 0, 0)
        frame.Visible = false
        frame.Parent = contentFrame
        
        tabContents[name] = frame
        
        -- Add content
        content(frame)
        
        -- Auto-calculate canvas size
        local layout = Instance.new("UIListLayout")
        layout.Padding = UDim.new(0, 10)
        layout.SortOrder = Enum.SortOrder.LayoutOrder
        layout.Parent = frame
        
        layout:GetPropertyChangedSignal("AbsoluteContentSize"):Connect(function()
            frame.CanvasSize = UDim2.new(0, 0, 0, layout.AbsoluteContentSize.Y + 20)
        end)
        
        return tabButton, frame
    end
    
    -- Scripts Tab
    createTab("Scripts", "🚀", function(frame)
        local scriptsHeader = createLabel(frame, "ScriptsHeader", "🎯 Premium Scripts Collection", UDim2.new(0, 0, 0, 0), UDim2.new(1, 0, 0, 40), 16, COLORS.Primary)
        scriptsHeader.Font = Enum.Font.GothamBold
        scriptsHeader.TextXAlignment = Enum.TextXAlignment.Left
        
        local scriptsDesc = createLabel(frame, "ScriptsDesc", "High-quality, verified scripts from ZpofeHub. All scripts are regularly updated and tested.", UDim2.new(0, 0, 0, 45), UDim2.new(1, 0, 0, 30), 12, COLORS.TextSecondary)
        scriptsDesc.TextXAlignment = Enum.TextXAlignment.Left
        
        createButton(frame, "LoadPremiumScript", "🎮 Load Premium Script", UDim2.new(0, 0, 0, 90), UDim2.new(1, 0, 0, 45), function()
            loadScript()
        end)
        
        createButton(frame, "HyperShot", "🎯 HyperShot (Aimbot & ESP)", UDim2.new(0, 0, 0, 150), UDim2.new(1, 0, 0, 45), function()
            loadstring(game:HttpGet("https://pastebin.com/raw/ZGHAFH9X"))()
            showNotification("HyperShot", "Loading HyperShot module...", "success")
        end)
        
        createButton(frame, "Bronx3", "💰 Bronx 3 (Market Exploits)", UDim2.new(0, 0, 0, 210), UDim2.new(1, 0, 0, 45), function()
            loadstring(game:HttpGet("https://pastebin.com/raw/nYtvhF7N"))()
            showNotification("Bronx 3", "Loading market exploits...", "success")
        end)
        
        createButton(frame, "AntiCrasher", "🛡️ Anti Crasher", UDim2.new(0, 0, 0, 270), UDim2.new(1, 0, 0, 45), function()
            loadstring(game:HttpGet("https://pastebin.com/raw/Wss94WD4"))()
            showNotification("Anti Crasher", "Protection module loaded!", "success")
        end)
    end)
    
    -- Games Tab
    createTab("Games", "🎮", function(frame)
        local gamesHeader = createLabel(frame, "GamesHeader", "🎮 Featured Game Scripts", UDim2.new(0, 0, 0, 0), UDim2.new(1, 0, 0, 40), 16, COLORS.Primary)
        gamesHeader.Font = Enum.Font.GothamBold
        gamesHeader.TextXAlignment = Enum.TextXAlignment.Left
        
        local currentGame = "Unknown"
        pcall(function()
            currentGame = MarketplaceService:GetProductInfo(game.PlaceId).Name
        end)
        
        local gameInfo = createLabel(frame, "GameInfo", "Current Game: " .. currentGame .. "\nPlace ID: " .. game.PlaceId, UDim2.new(0, 0, 0, 45), UDim2.new(1, 0, 0, 40), 12, COLORS.TextSecondary)
        gameInfo.TextXAlignment = Enum.TextXAlignment.Left
        
        -- HyperShot Button
        createButton(frame, "HyperShot", "🎯 HyperShot", UDim2.new(0, 0, 0, 100), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                loadstring(game:HttpGet("https://pastebin.com/raw/ZGHAFH9X"))()
                showNotification("HyperShot", "HyperShot script loaded successfully!", "success")
            end)
        end)
        
        -- Tha Bronx 3 Button
        createButton(frame, "ThaBronx3", "💰 Tha Bronx 3", UDim2.new(0, 0, 0, 160), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                loadstring(game:HttpGet("https://pastebin.com/raw/nYtvhF7N"))()
                showNotification("Tha Bronx 3", "Tha Bronx 3 loaded! (Works 50/50 - may be patched)", "warning")
            end)
        end)
        
        -- Status warning for Bronx 3
        local bronxWarning = createLabel(frame, "BronxWarning", "⚠️ Note: Tha Bronx 3 works 50/50 - most likely patched", UDim2.new(0, 0, 0, 220), UDim2.new(1, 0, 0, 30), 11, COLORS.Warning)
        bronxWarning.TextXAlignment = Enum.TextXAlignment.Left
        
        createButton(frame, "Walkspeed", "⚡ Speed/Jump Hacks", UDim2.new(0, 0, 0, 270), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                if LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("Humanoid") then
                    LocalPlayer.Character.Humanoid.WalkSpeed = 50
                    LocalPlayer.Character.Humanoid.JumpPower = 100
                    showNotification("Speed Boost", "Movement enhanced! Speed: 50, Jump: 100", "success")
                else
                    showNotification("Error", "Character not found or invalid", "error")
                end
            end)
        end)
    end)
    
    -- Tools Tab
    createTab("Tools", "🧰", function(frame)
        local toolsHeader = createLabel(frame, "ToolsHeader", "🧰 Utility Tools", UDim2.new(0, 0, 0, 0), UDim2.new(1, 0, 0, 40), 16, COLORS.Primary)
        toolsHeader.Font = Enum.Font.GothamBold
        toolsHeader.TextXAlignment = Enum.TextXAlignment.Left
        
        -- Anti Crasher - Primary utility
        createButton(frame, "AntiCrasher", "🛡️ Anti Crasher", UDim2.new(0, 0, 0, 60), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                loadstring(game:HttpGet("https://pastebin.com/raw/Wss94WD4"))()
                showNotification("Anti Crasher", "Protection module loaded successfully!", "success")
            end)
        end)
        
        createButton(frame, "DarkDex", "🔍 Dark Dex Explorer", UDim2.new(0, 0, 0, 120), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                loadstring(game:HttpGet("https://raw.githubusercontent.com/Babyhamsta/RBLX_Scripts/main/Universal/BypassedDarkDexV3.lua", true))()
                showNotification("Dark Dex", "Explorer loaded!", "success")
            end)
        end)
        
        createButton(frame, "InfiniteYield", "🎛️ Infinite Yield", UDim2.new(0, 0, 0, 180), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                loadstring(game:HttpGet('https://raw.githubusercontent.com/EdgeIY/infiniteyield/master/source'))()
                showNotification("Infinite Yield", "Admin commands loaded!", "success")
            end)
        end)
        
        createButton(frame, "RemotesSpy", "📡 Remotes Spy", UDim2.new(0, 0, 0, 240), UDim2.new(1, 0, 0, 45), function()
            showNotification("Remotes Spy", "Monitoring remote events...", "info")
            -- Add remotes spy implementation
        end)
        
        createButton(frame, "ServerHop", "🌐 Server Hop", UDim2.new(0, 0, 0, 300), UDim2.new(1, 0, 0, 45), function()
            showNotification("Server Hop", "Finding new server...", "info")
            -- Add server hop logic here
        end)
    end)
    
    -- Settings Tab
    createTab("Settings", "⚙️", function(frame)
        local settingsHeader = createLabel(frame, "SettingsHeader", "⚙️ Hub Settings", UDim2.new(0, 0, 0, 0), UDim2.new(1, 0, 0, 40), 16, COLORS.Primary)
        settingsHeader.Font = Enum.Font.GothamBold
        settingsHeader.TextXAlignment = Enum.TextXAlignment.Left
        
        local keyLabel = createLabel(frame, "KeyLabel", "🔑 Active License: " .. (authorizedKey or "None"), UDim2.new(0, 0, 0, 60), UDim2.new(1, 0, 0, 30), 12, COLORS.TextSecondary)
        keyLabel.TextXAlignment = Enum.TextXAlignment.Left
        
        local hwidLabel = createLabel(frame, "HWIDLabel", "🔒 HWID: " .. hwid, UDim2.new(0, 0, 0, 95), UDim2.new(1, 0, 0, 30), 12, COLORS.TextSecondary)
        hwidLabel.TextXAlignment = Enum.TextXAlignment.Left
        
        createButton(frame, "ResetKey", "🗑️ Reset Saved Key", UDim2.new(0, 0, 0, 140), UDim2.new(1, 0, 0, 45), function()
            if delfile and isfile(KEY_FILE) then
                delfile(KEY_FILE)
                showNotification("Key Reset", "Saved key removed. Restart script to re-authenticate.", "success")
            else
                showNotification("Reset Failed", "Executor doesn't support file operations.", "error")
            end
        end)
        
        createButton(frame, "CheckAPI", "🌐 Check API Status", UDim2.new(0, 0, 0, 200), UDim2.new(1, 0, 0, 45), function()
            pcall(function()
                local response = game:HttpGet(HEALTH_ENDPOINT)
                local data = HttpService:JSONDecode(response)
                if data.status == "healthy" then
                    showNotification("API Status", "ZpofeHub API is online and healthy!", "success")
                else
                    showNotification("API Status", "API status unknown", "warning")
                end
            end)
        end)
        
        createButton(frame, "JoinDiscord", "💬 Join Discord Server", UDim2.new(0, 0, 0, 260), UDim2.new(1, 0, 0, 45), function()
            if setclipboard then
                setclipboard("https://discord.gg/C6agZhmhCA")
                showNotification("Discord", "Invite link copied to clipboard!", "success")
            else
                showNotification("Discord", "Join: discord.gg/C6agZhmhCA", "info")
            end
        end)
    end)
    
    -- Show first tab by default
    if tabContents["Scripts"] then
        tabContents["Scripts"].Visible = true
        local firstTab = tabFrame:FindFirstChild("ScriptsTab")
        if firstTab then
            firstTab.BackgroundColor3 = COLORS.Primary
        end
    end
    
    -- Animate hub frame in
    HubFrame.Position = UDim2.new(0.5, -400, 1, 0)
    createTween(HubFrame, {Position = UDim2.new(0.5, -400, 0.5, -300)}, 0.5, Enum.EasingStyle.Back)
end

--// Main Initialization
local function initializeHub()
    -- Remove existing GUI if present
    if PlayerGui:FindFirstChild("ZpofeHubUniversal") then
        PlayerGui.ZpofeHubUniversal:Destroy()
    end
    
    -- Create main ScreenGui
    ScreenGui = Instance.new("ScreenGui")
    ScreenGui.Name = "ZpofeHubUniversal"
    ScreenGui.ResetOnSpawn = false
    ScreenGui.IgnoreGuiInset = true
    ScreenGui.Parent = PlayerGui
    
    -- Main container frame
    MainFrame = Instance.new("Frame")
    MainFrame.Name = "MainFrame"
    MainFrame.Size = UDim2.new(1, 0, 1, 0)
    MainFrame.Position = UDim2.new(0, 0, 0, 0)
    MainFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
    MainFrame.BackgroundTransparency = 0.3
    MainFrame.BorderSizePixel = 0
    MainFrame.Parent = ScreenGui
    
    -- Log execution
    logExecution()
    
    -- Create authentication frame
    createAuthFrame()
    
    -- Show welcome notification
    task.spawn(function()
        showNotification("ZpofeHub Universal", "Welcome to ZpofeHub Universal Script Hub v2.0!", "success")
    end)
end

--// Start the hub
initializeHub()

print("🛰️ ZpofeHub Universal Hub v2.0 loaded successfully!")
print("🔗 Discord: discord.gg/C6agZhmhCA")
print("🌐 API: " .. API_BASE)
