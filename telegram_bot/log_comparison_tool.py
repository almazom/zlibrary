#!/usr/bin/env python3
"""
Log Comparison Tool - Compare manual vs UC automated message logs
This tool helps identify exactly why automated messages don't trigger book search
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class LogAnalyzer:
    def __init__(self, log_file: str = "bot_tdd.log"):
        self.log_file = Path(log_file)
        self.manual_sessions = []
        self.uc_sessions = []
        
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """Parse a single log line into components"""
        # Pattern: 2025-08-12 14:52:50,513 | __main__ | INFO | Message
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| ([^|]+) \| ([^|]+) \| (.+)'
        match = re.match(pattern, line.strip())
        
        if match:
            timestamp_str, module, level, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            
            return {
                'timestamp': timestamp,
                'module': module.strip(),
                'level': level.strip(),
                'message': message.strip(),
                'raw_line': line
            }
        return None
    
    def identify_session_type(self, log_entry: Dict[str, Any]) -> str:
        """Identify if this log entry is from manual or UC automated session"""
        message = log_entry['message']
        
        # UC automated indicators
        uc_indicators = [
            "UC22:", "UC23:", "UC2:", 
            "Telegram Bot Basic",
            "Book Request - ",
            "send_message",
            "Monitoring responses",
            "TEST 1:", "TEST 2:",
            "API connection"
        ]
        
        for indicator in uc_indicators:
            if indicator in message:
                return "uc_automated"
        
        # Manual session indicators (actual bot processing)
        manual_indicators = [
            "Received message from user",
            "Processing book request from user", 
            "Searching for book:",
            "Sending EPUB file:",
            "EPUB file sent successfully"
        ]
        
        for indicator in manual_indicators:
            if indicator in message:
                return "manual"
                
        return "unknown"
    
    def extract_sessions(self) -> None:
        """Extract separate manual and UC sessions from logs"""
        if not self.log_file.exists():
            print(f"❌ Log file not found: {self.log_file}")
            return
            
        current_manual_session = []
        current_uc_session = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if not parsed:
                    continue
                
                session_type = self.identify_session_type(parsed)
                
                if session_type == "manual":
                    # If we have a previous UC session, save it
                    if current_uc_session:
                        self.uc_sessions.append(current_uc_session)
                        current_uc_session = []
                    current_manual_session.append(parsed)
                    
                elif session_type == "uc_automated":
                    # If we have a previous manual session, save it
                    if current_manual_session:
                        self.manual_sessions.append(current_manual_session)
                        current_manual_session = []
                    current_uc_session.append(parsed)
                    
                # For unknown entries, add to current session if any exists
                elif session_type == "unknown":
                    if current_manual_session:
                        current_manual_session.append(parsed)
                    elif current_uc_session:
                        current_uc_session.append(parsed)
        
        # Save final sessions
        if current_manual_session:
            self.manual_sessions.append(current_manual_session)
        if current_uc_session:
            self.uc_sessions.append(current_uc_session)
    
    def analyze_session_flow(self, session: List[Dict[str, Any]], session_type: str) -> Dict[str, Any]:
        """Analyze the flow of events in a session"""
        analysis = {
            'session_type': session_type,
            'total_logs': len(session),
            'start_time': session[0]['timestamp'] if session else None,
            'end_time': session[-1]['timestamp'] if session else None,
            'duration_seconds': 0,
            'stages': {
                'message_received': False,
                'processing_started': False,
                'progress_message_sent': False,
                'search_started': False,
                'search_completed': False,
                'epub_sent': False,
                'errors': []
            },
            'detailed_flow': [],
            'missing_stages': []
        }
        
        if len(session) < 2:
            return analysis
            
        # Calculate duration
        analysis['duration_seconds'] = (session[-1]['timestamp'] - session[0]['timestamp']).total_seconds()
        
        # Analyze each log entry
        for entry in session:
            message = entry['message']
            stage_info = {
                'timestamp': entry['timestamp'],
                'message': message[:100] + "..." if len(message) > 100 else message,
                'level': entry['level']
            }
            analysis['detailed_flow'].append(stage_info)
            
            # Identify stages
            if "Received message from user" in message or "TEXT RESPONSE:" in message:
                analysis['stages']['message_received'] = True
            
            if "Processing book request" in message:
                analysis['stages']['processing_started'] = True
                
            if "PROGRESS MESSAGE:" in message or "🔍" in message:
                analysis['stages']['progress_message_sent'] = True
                
            if "Searching for book:" in message:
                analysis['stages']['search_started'] = True
                
            if "Script returncode:" in message or "found" in message.lower():
                analysis['stages']['search_completed'] = True
                
            if "Sending EPUB file:" in message or "EPUB DOCUMENT RECEIVED" in message:
                analysis['stages']['epub_sent'] = True
                
            if entry['level'] in ['ERROR', 'WARNING']:
                analysis['stages']['errors'].append(message)
        
        # Identify missing stages
        expected_stages = ['message_received', 'processing_started', 'progress_message_sent', 'search_started']
        for stage, present in analysis['stages'].items():
            if stage in expected_stages and not present:
                analysis['missing_stages'].append(stage)
                
        return analysis
    
    def compare_sessions(self) -> None:
        """Compare manual vs UC automated sessions"""
        print("=" * 80)
        print("🔍 LOG COMPARISON ANALYSIS")
        print("=" * 80)
        
        print(f"\n📊 SESSION SUMMARY:")
        print(f"   Manual sessions found: {len(self.manual_sessions)}")
        print(f"   UC automated sessions found: {len(self.uc_sessions)}")
        
        # Analyze latest sessions
        if self.manual_sessions:
            latest_manual = self.analyze_session_flow(self.manual_sessions[-1], "manual")
            print(f"\n✅ LATEST MANUAL SESSION:")
            self.print_session_analysis(latest_manual)
            
        if self.uc_sessions:
            latest_uc = self.analyze_session_flow(self.uc_sessions[-1], "uc_automated")  
            print(f"\n🤖 LATEST UC AUTOMATED SESSION:")
            self.print_session_analysis(latest_uc)
            
        # Compare and identify differences
        if self.manual_sessions and self.uc_sessions:
            self.identify_key_differences(latest_manual, latest_uc)
    
    def print_session_analysis(self, analysis: Dict[str, Any]) -> None:
        """Print detailed session analysis"""
        print(f"   Duration: {analysis['duration_seconds']:.2f} seconds")
        print(f"   Total log entries: {analysis['total_logs']}")
        
        print(f"   Stages completed:")
        for stage, completed in analysis['stages'].items():
            if stage == 'errors':
                continue
            status = "✅" if completed else "❌"
            print(f"     {status} {stage.replace('_', ' ').title()}")
            
        if analysis['missing_stages']:
            print(f"   ⚠️ Missing stages: {', '.join(analysis['missing_stages'])}")
            
        if analysis['stages']['errors']:
            print(f"   🚨 Errors detected: {len(analysis['stages']['errors'])}")
            for error in analysis['stages']['errors'][:3]:  # Show first 3 errors
                print(f"     - {error[:80]}...")
        
        print(f"   📝 Flow timeline:")
        for i, flow in enumerate(analysis['detailed_flow'][:10]):  # Show first 10 entries
            print(f"     {i+1:2d}. [{flow['level']:5s}] {flow['message']}")
        
        if len(analysis['detailed_flow']) > 10:
            print(f"     ... ({len(analysis['detailed_flow']) - 10} more entries)")
    
    def identify_key_differences(self, manual: Dict[str, Any], uc: Dict[str, Any]) -> None:
        """Identify key differences between manual and UC sessions"""
        print(f"\n🔍 KEY DIFFERENCES ANALYSIS:")
        print("=" * 50)
        
        # Stage completion comparison
        manual_stages = manual['stages']
        uc_stages = uc['stages']
        
        stage_differences = []
        for stage in ['message_received', 'processing_started', 'progress_message_sent', 'search_started', 'search_completed', 'epub_sent']:
            manual_has = manual_stages.get(stage, False)
            uc_has = uc_stages.get(stage, False)
            
            if manual_has != uc_has:
                stage_differences.append({
                    'stage': stage,
                    'manual': manual_has,
                    'uc': uc_has
                })
        
        if stage_differences:
            print("📊 Stage Completion Differences:")
            for diff in stage_differences:
                manual_status = "✅" if diff['manual'] else "❌"
                uc_status = "✅" if diff['uc'] else "❌" 
                print(f"   {diff['stage'].replace('_', ' ').title()}:")
                print(f"     Manual: {manual_status}")
                print(f"     UC Auto: {uc_status}")
                
        # Duration comparison
        print(f"\n⏱️ Duration Comparison:")
        print(f"   Manual: {manual['duration_seconds']:.2f}s")
        print(f"   UC Auto: {uc['duration_seconds']:.2f}s")
        print(f"   Difference: {abs(manual['duration_seconds'] - uc['duration_seconds']):.2f}s")
        
        # Error comparison
        manual_errors = len(manual['stages']['errors'])
        uc_errors = len(uc['stages']['errors'])
        
        print(f"\n🚨 Error Count Comparison:")
        print(f"   Manual errors: {manual_errors}")
        print(f"   UC Auto errors: {uc_errors}")
        
        # Critical findings
        print(f"\n🎯 CRITICAL FINDINGS:")
        
        if not uc_stages.get('search_started', False) and manual_stages.get('search_started', False):
            print("   ❌ CRITICAL: UC automated messages DO NOT trigger book search!")
            print("   ✅ Manual messages DO trigger book search")
            print("   📋 Root cause: Message processing pipeline differs between methods")
            
        if not uc_stages.get('progress_message_sent', False) and manual_stages.get('progress_message_sent', False):
            print("   ❌ CRITICAL: UC automated flow missing progress messages!")
            print("   💡 This indicates polling conflicts prevent bot response")
            
        print(f"\n💡 RECOMMENDED SOLUTION:")
        print("   1. Use webhook mode instead of polling to avoid conflicts")
        print("   2. Implement message queuing for UC tests")
        print("   3. Add retry mechanisms for progress messages")
        print("   4. Separate UC test environment from production bot")

def main():
    """Main function to run log analysis"""
    print("🔍 Starting Log Comparison Analysis...")
    
    # Check for log files
    log_files = ['bot_tdd.log', 'debug_bot.log', 'bot_webhook.log']
    found_logs = [f for f in log_files if Path(f).exists()]
    
    if not found_logs:
        print("❌ No log files found. Expected files: bot_tdd.log, debug_bot.log, bot_webhook.log")
        return
    
    print(f"📁 Found log files: {', '.join(found_logs)}")
    
    for log_file in found_logs:
        print(f"\n" + "="*80)
        print(f"📄 ANALYZING: {log_file}")
        print("="*80)
        
        analyzer = LogAnalyzer(log_file)
        analyzer.extract_sessions()
        analyzer.compare_sessions()

if __name__ == '__main__':
    main()