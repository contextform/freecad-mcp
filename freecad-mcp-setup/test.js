#!/usr/bin/env node

const { checkForUpdates, getCurrentVersion } = require('./index.js');

async function test() {
  console.log('🧪 Testing FreeCAD MCP Setup\n');
  
  try {
    // Test version checking
    console.log('Current version:', getCurrentVersion() || 'Not installed');
    
    // Test GitHub API
    console.log('Testing GitHub API...');
    const result = await checkForUpdates();
    console.log('Update check result:', result.shouldUpdate ? 'Update available' : 'Up to date');
    
    console.log('\n✅ All tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

test();