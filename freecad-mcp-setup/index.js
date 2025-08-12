#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');
const https = require('https');

const REPO = 'contextform/freecad-mcp';
const VERSION_FILE = path.join(os.homedir(), '.freecad-mcp-version');

// Colors for console output
const colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logStep(step, message) {
  log(`${step} ${message}`, 'blue');
}

function logSuccess(message) {
  log(`✅ ${message}`, 'green');
}

function logWarning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function logError(message) {
  log(`❌ ${message}`, 'red');
}

// Get OS-specific FreeCAD Mod directory
function getFreeCadModDir() {
  const platform = os.platform();
  const home = os.homedir();
  
  switch (platform) {
    case 'darwin': // macOS
      return path.join(home, 'Library/Application Support/FreeCAD/Mod');
    case 'linux':
      return path.join(home, '.local/share/FreeCAD/Mod');
    case 'win32':
      return path.join(home, 'AppData/Roaming/FreeCAD/Mod');
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}

// Check if FreeCAD is installed
function checkFreeCadInstallation() {
  const platform = os.platform();
  
  try {
    if (platform === 'darwin') {
      return fs.existsSync('/Applications/FreeCAD.app');
    } else if (platform === 'linux') {
      execSync('which freecad', { stdio: 'ignore' });
      return true;
    } else if (platform === 'win32') {
      // Check common Windows installation paths
      const commonPaths = [
        'C:\\Program Files\\FreeCAD\\bin\\FreeCAD.exe',
        'C:\\Program Files (x86)\\FreeCAD\\bin\\FreeCAD.exe',
        'C:\\FreeCAD\\bin\\FreeCAD.exe',
        path.join(home, 'AppData\\Local\\FreeCAD\\FreeCAD.exe')
      ];
      
      // First try common paths
      if (commonPaths.some(p => fs.existsSync(p))) {
        return true;
      }
      
      // Try to find FreeCAD in PATH
      try {
        execSync('where freecad', { stdio: 'ignore' });
        return true;
      } catch {
        // Try alternative command
        try {
          execSync('freecad --version', { stdio: 'ignore' });
          return true;
        } catch {
          return false;
        }
      }
    }
  } catch (error) {
    return false;
  }
  
  return false;
}

// Fetch latest release info from GitHub
async function fetchLatestRelease() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      path: `/repos/${REPO}/releases/latest`,
      headers: { 'User-Agent': 'freecad-mcp-setup' }
    };
    
    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', reject);
  });
}

// Get currently installed version
function getCurrentVersion() {
  try {
    if (fs.existsSync(VERSION_FILE)) {
      return fs.readFileSync(VERSION_FILE, 'utf8').trim();
    }
  } catch (error) {
    // Ignore errors, assume no version installed
  }
  return null;
}

// Save current version
function saveCurrentVersion(version) {
  try {
    fs.writeFileSync(VERSION_FILE, version);
  } catch (error) {
    logWarning(`Could not save version info: ${error.message}`);
  }
}

// Check for updates and prompt user
async function checkForUpdates() {
  try {
    logStep('🔍', 'Checking for updates...');
    
    const release = await fetchLatestRelease();
    const latestVersion = release.tag_name;
    const currentVersion = getCurrentVersion();
    
    if (!currentVersion) {
      log(`Installing FreeCAD MCP ${latestVersion}`, 'blue');
      return { shouldUpdate: true, release };
    }
    
    if (latestVersion === currentVersion) {
      logSuccess(`Already up to date (${currentVersion})`);
      return { shouldUpdate: false };
    }
    
    logWarning(`New version available: ${currentVersion} → ${latestVersion}`);
    log('\nRelease notes:');
    log(release.body || 'No release notes available');
    
    // In a real CLI, we'd use readline for interactive prompt
    // For now, we'll auto-update with a message
    log('\nTo update, run: freecad-mcp setup --update', 'blue');
    
    // Check if --update flag was passed
    if (process.argv.includes('--update')) {
      return { shouldUpdate: true, release };
    }
    
    return { shouldUpdate: false };
    
  } catch (error) {
    logWarning(`Could not check for updates: ${error.message}`);
    logWarning('Proceeding with installation...');
    return { shouldUpdate: true, release: null };
  }
}

// Download and extract release
async function downloadAndInstall(release) {
  const modDir = getFreeCadModDir();
  const aiCopilotDir = path.join(modDir, 'AICopilot');
  
  logStep('📁', `Installing to: ${aiCopilotDir}`);
  
  try {
    // Download from GitHub repository
    const tempDir = path.join(os.tmpdir(), 'freecad-mcp-temp');
    
    // Clean up temp directory if it exists
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
    fs.mkdirSync(tempDir, { recursive: true });
    
    // Download and extract repository
    await downloadAndExtractRepo(tempDir);
    
    // List contents for debugging
    logStep('📋', `Temp directory contents: ${fs.readdirSync(tempDir).join(', ')}`);
    
    // Find the AICopilot directory in extracted files
    const extractedDir = findAICopilotDir(tempDir);
    if (!extractedDir) {
      logError('AICopilot workbench not found in downloaded files');
      logError('This might be a ZIP extraction issue on Windows');
      logError('Please try the manual installation method from the README');
      throw new Error('AICopilot workbench not found in downloaded files');
    }
    
    // Create Mod directory if it doesn't exist
    fs.mkdirSync(modDir, { recursive: true });
    
    // Copy AICopilot directory
    copyDirectory(extractedDir, aiCopilotDir);
    
    // Clean up temp directory
    fs.rmSync(tempDir, { recursive: true, force: true });
    
    logSuccess('FreeCAD workbench installed');
    
  } catch (error) {
    logError(`Installation failed: ${error.message}`);
    throw error;
  }
}

// Download and extract GitHub repository
async function downloadAndExtractRepo(tempDir) {
  return new Promise((resolve, reject) => {
    const zipUrl = `https://github.com/${REPO}/archive/refs/heads/main.zip`;
    const zipPath = path.join(tempDir, 'repo.zip');
    
    logStep('⬇️', 'Downloading FreeCAD MCP...');
    
    const file = fs.createWriteStream(zipPath);
    https.get(zipUrl, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        // Follow redirect
        https.get(response.headers.location, (redirectResponse) => {
          redirectResponse.pipe(file);
          file.on('finish', () => {
            file.close();
            extractZip(zipPath, tempDir).then(resolve).catch(reject);
          });
        }).on('error', reject);
      } else {
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          extractZip(zipPath, tempDir).then(resolve).catch(reject);
        });
      }
    }).on('error', reject);
  });
}

// Extract ZIP file using pure Node.js (no PowerShell/unzip dependencies)
async function extractZip(zipPath, extractDir) {
  try {
    logStep('📦', `Extracting ZIP file: ${zipPath}`);
    logStep('📋', `ZIP file size: ${fs.statSync(zipPath).size} bytes`);
    
    const AdmZip = require('adm-zip');
    const zip = new AdmZip(zipPath);
    
    // List ZIP contents for debugging
    const zipEntries = zip.getEntries();
    logStep('📂', `ZIP contains ${zipEntries.length} entries`);
    
    if (zipEntries.length > 0) {
      logStep('📝', `First few entries: ${zipEntries.slice(0, 3).map(e => e.entryName).join(', ')}`);
    }
    
    zip.extractAllTo(extractDir, true);
    
    // Verify extraction
    const extractedItems = fs.readdirSync(extractDir);
    logStep('✅', `Extracted ${extractedItems.length} items to: ${extractDir}`);
    
    fs.unlinkSync(zipPath); // Clean up zip file
    logSuccess('ZIP extraction completed');
  } catch (error) {
    logError(`ZIP extraction error: ${error.message}`);
    logError(`ZIP path: ${zipPath}`);
    logError(`Extract dir: ${extractDir}`);
    throw new Error(`Failed to extract archive: ${error.message}`);
  }
}

// Find AICopilot directory in extracted files
function findAICopilotDir(tempDir) {
  function searchRecursively(dir, depth = 0) {
    try {
      const items = fs.readdirSync(dir);
      logStep('🔍', `Searching in: ${dir} (${items.length} items, depth: ${depth})`);
      
      for (const item of items) {
        const itemPath = path.join(dir, item);
        
        if (fs.statSync(itemPath).isDirectory()) {
          logStep('📁', `Found directory: ${item}`);
          if (item === 'AICopilot') {
            logStep('✅', `Found AICopilot at: ${itemPath}`);
            return itemPath;
          }
          
          // Only search 2 levels deep to avoid infinite loops
          if (depth < 2) {
            const found = searchRecursively(itemPath, depth + 1);
            if (found) return found;
          }
        }
      }
    } catch (error) {
      logError(`Error searching directory ${dir}: ${error.message}`);
    }
    
    return null;
  }
  
  return searchRecursively(tempDir);
}

// Download a single file
async function downloadFile(url, filePath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filePath);
    
    https.get(url, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        // Follow redirect
        https.get(response.headers.location, (redirectResponse) => {
          redirectResponse.pipe(file);
          file.on('finish', () => {
            file.close();
            resolve();
          });
        }).on('error', reject);
      } else {
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve();
        });
      }
    }).on('error', reject);
  });
}

// Utility function to copy directory recursively
function copyDirectory(src, dest) {
  if (fs.existsSync(dest)) {
    // Remove existing directory
    fs.rmSync(dest, { recursive: true, force: true });
  }
  
  fs.mkdirSync(dest, { recursive: true });
  
  const items = fs.readdirSync(src);
  for (const item of items) {
    const srcPath = path.join(src, item);
    const destPath = path.join(dest, item);
    
    if (fs.statSync(srcPath).isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Register MCP server with Claude Code
async function registerMCPServer() {
  try {
    logStep('🔧', 'Registering MCP server with Claude Code...');
    
    // Check if Claude Code is installed
    try {
      execSync('claude --version', { stdio: 'ignore' });
    } catch (error) {
      logWarning('Claude Code not found. Please install it first:');
      log('npm install -g claude-code', 'blue');
      return false;
    }
    
    // Download working_bridge.py to a persistent location
    const bridgeDir = path.join(os.homedir(), '.freecad-mcp');
    const bridgePath = path.join(bridgeDir, 'working_bridge.py');
    
    fs.mkdirSync(bridgeDir, { recursive: true });
    
    if (!fs.existsSync(bridgePath)) {
      logStep('⬇️', 'Downloading MCP bridge server...');
      await downloadFile(
        `https://raw.githubusercontent.com/${REPO}/main/working_bridge.py`,
        bridgePath
      );
    }
    
    // Register the server with platform-appropriate Python command
    const pythonCmd = os.platform() === 'win32' ? 'python' : 'python3';
    const command = `claude mcp add freecad ${pythonCmd} "${bridgePath}"`;
    execSync(command, { stdio: 'inherit' });
    
    logSuccess('MCP server registered with Claude Code');
    return true;
    
  } catch (error) {
    logError(`Failed to register MCP server: ${error.message}`);
    return false;
  }
}

// Test the connection
async function testConnection() {
  logStep('🧪', 'Testing connection...');
  
  log('Please follow these steps to test:');
  log('1. Launch FreeCAD', 'blue');
  log('2. In a new terminal, run: claude', 'blue');
  log('3. Ask Claude: "List available tools"', 'blue');
  log('4. You should see mcp__freecad__* tools', 'blue');
}

// Main installation function
async function install() {
  try {
    log('🚀 FreeCAD MCP Setup\n', 'blue');
    
    // Check FreeCAD installation (non-blocking)
    logStep('1️⃣', 'Checking FreeCAD installation...');
    if (!checkFreeCadInstallation()) {
      logWarning('FreeCAD not detected, but continuing installation...');
      logWarning('Make sure FreeCAD 1.0+ is installed: https://freecad.org/downloads.php');
    } else {
      logSuccess('FreeCAD found');
    }
    
    // Check for updates
    const { shouldUpdate, release } = await checkForUpdates();
    
    if (shouldUpdate) {
      logStep('2️⃣', 'Installing FreeCAD MCP...');
      await downloadAndInstall(release);
      
      if (release && release.tag_name) {
        saveCurrentVersion(release.tag_name);
      } else {
        saveCurrentVersion('latest');
      }
    }
    
    // Register MCP server
    logStep('3️⃣', 'Setting up Claude integration...');
    const registered = await registerMCPServer();
    
    if (!registered) {
      log('\nManual registration required:', 'yellow');
      log('claude mcp add freecad python3 /path/to/working_bridge.py', 'blue');
    }
    
    // Test connection
    await testConnection();
    
    log('\n🎉 Installation complete!', 'green');
    log('Happy CAD designing with AI! 🤖', 'blue');
    
  } catch (error) {
    logError(`Installation failed: ${error.message}`);
    process.exit(1);
  }
}

// Handle command line arguments
function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
FreeCAD MCP Setup - Easy installer for FreeCAD MCP

Usage:
  freecad-mcp setup          Install or check for updates
  freecad-mcp setup --update Force update to latest version
  freecad-mcp --help         Show this help

For more information, visit:
https://github.com/contextform/freecad-mcp
    `);
    return;
  }
  
  if (args[0] === 'setup' || args.length === 0) {
    install();
  } else {
    logError(`Unknown command: ${args[0]}`);
    log('Run "freecad-mcp --help" for usage information');
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { install, checkForUpdates, getCurrentVersion };