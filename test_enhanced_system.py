#!/usr/bin/env python3
"""
Test script for Enhanced QIRAT AI System
Tests authentication system and 5-second segment analysis
"""

import os
import sys
import tempfile
import numpy as np
import soundfile as sf
from auth_system import AuthSystem
from enhanced_pitch_analysis import (
    analyze_5second_segments, 
    generate_segment_feedback,
    create_segment_visualization
)

def create_test_audio(duration=10.0, sample_rate=22050, frequency=440.0):
    """Create a test audio file with a specific frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.sin(2 * np.pi * frequency * t)
    return audio, sample_rate

def create_test_audio_with_variations(duration=10.0, sample_rate=22050):
    """Create test audio with pitch variations"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create audio with different frequencies in different segments
    audio = np.zeros_like(t)
    
    # Segment 1 (0-2s): 440 Hz
    mask1 = (t >= 0) & (t < 2)
    audio[mask1] = np.sin(2 * np.pi * 440 * t[mask1])
    
    # Segment 2 (2-4s): 450 Hz (slightly higher)
    mask2 = (t >= 2) & (t < 4)
    audio[mask2] = np.sin(2 * np.pi * 450 * t[mask2])
    
    # Segment 3 (4-6s): 430 Hz (slightly lower)
    mask3 = (t >= 4) & (t < 6)
    audio[mask3] = np.sin(2 * np.pi * 430 * t[mask3])
    
    # Segment 4 (6-8s): 440 Hz (back to reference)
    mask4 = (t >= 6) & (t < 8)
    audio[mask4] = np.sin(2 * np.pi * 440 * t[mask4])
    
    # Segment 5 (8-10s): 460 Hz (higher)
    mask5 = (t >= 8) & (t < 10)
    audio[mask5] = np.sin(2 * np.pi * 460 * t[mask5])
    
    return audio, sample_rate

def test_authentication_system():
    """Test the authentication system"""
    print("🔐 Testing Authentication System...")
    
    # Create temporary database
    test_db = "test_users.db"
    auth_system = AuthSystem(test_db)
    
    try:
        # Test user registration
        print("  Testing user registration...")
        success, result = auth_system.register_user("testuser", "test@example.com", "testpassword123")
        assert success, f"Registration failed: {result}"
        print("  ✅ User registration successful")
        
        # Test duplicate registration
        success, result = auth_system.register_user("testuser", "test@example.com", "testpassword123")
        assert not success, "Duplicate registration should fail"
        print("  ✅ Duplicate registration correctly rejected")
        
        # Test login
        print("  Testing user login...")
        success, result = auth_system.login_user("testuser", "testpassword123")
        assert success, f"Login failed: {result}"
        assert result['username'] == "testuser"
        assert result['email'] == "test@example.com"
        print("  ✅ User login successful")
        
        # Test wrong password
        success, result = auth_system.login_user("testuser", "wrongpassword")
        assert not success, "Wrong password login should fail"
        print("  ✅ Wrong password correctly rejected")
        
        # Test password reset token creation
        print("  Testing password reset...")
        success, result = auth_system.create_reset_token("test@example.com")
        assert success, f"Reset token creation failed: {result}"
        token = result['token']
        print("  ✅ Password reset token created")
        
        # Test password reset
        success, result = auth_system.reset_password(token, "newpassword123")
        assert success, f"Password reset failed: {result}"
        print("  ✅ Password reset successful")
        
        # Test login with new password
        success, result = auth_system.login_user("testuser", "newpassword123")
        assert success, "Login with new password should work"
        print("  ✅ Login with new password successful")
        
        print("✅ Authentication system tests passed!")
        
    except Exception as e:
        print(f"❌ Authentication system test failed: {e}")
        return False
    
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)
    
    return True

def test_5second_segment_analysis():
    """Test the 5-second segment analysis"""
    print("🎵 Testing 5-Second Segment Analysis...")
    
    try:
        # Create test audio files
        print("  Creating test audio files...")
        
        # Reference audio (440 Hz throughout)
        ref_audio, ref_sr = create_test_audio(duration=10.0, frequency=440.0)
        ref_file = "test_reference.wav"
        sf.write(ref_file, ref_audio, ref_sr)
        
        # User audio with variations
        user_audio, user_sr = create_test_audio_with_variations(duration=10.0)
        user_file = "test_user.wav"
        sf.write(user_file, user_audio, user_sr)
        
        print("  ✅ Test audio files created")
        
        # Test 5-second segment analysis
        print("  Testing segment analysis...")
        segments_data = analyze_5second_segments(user_file, ref_file, threshold=5)
        
        # Should find segments with differences
        assert len(segments_data) > 0, "Should detect segments with pitch differences"
        print(f"  ✅ Found {len(segments_data)} segments with differences")
        
        # Test segment feedback generation
        print("  Testing feedback generation...")
        feedback = generate_segment_feedback(segments_data)
        
        assert 'total_segments' in feedback
        assert 'segments_with_issues' in feedback
        assert 'overall_summary' in feedback
        assert 'recommendations' in feedback
        print("  ✅ Feedback generation successful")
        
        # Test visualization creation
        print("  Testing visualization creation...")
        fig = create_segment_visualization(segments_data)
        assert fig is not None, "Visualization should be created"
        print("  ✅ Visualization creation successful")
        
        # Verify segment data structure
        for segment in segments_data:
            assert 'segment_id' in segment
            assert 'start_time' in segment
            assert 'end_time' in segment
            assert 'differences' in segment
            assert 'statistics' in segment
            assert 'user_pitch_contour' in segment
            assert 'ref_pitch_contour' in segment
        
        print("  ✅ Segment data structure verified")
        
        # Test specific segment analysis
        print("  Testing individual segment analysis...")
        for segment in segments_data:
            stats = segment['statistics']
            assert 'average_deviation_hz' in stats
            assert 'accuracy_percentage' in stats
            assert 'high_pitch_count' in stats
            assert 'low_pitch_count' in stats
            
            # Check that segments with differences have issues
            if len(segment['differences']) > 0:
                assert stats['average_deviation_hz'] > 0
                assert stats['accuracy_percentage'] < 100
        
        print("  ✅ Individual segment analysis verified")
        
        print("✅ 5-Second segment analysis tests passed!")
        
    except Exception as e:
        print(f"❌ 5-Second segment analysis test failed: {e}")
        return False
    
    finally:
        # Clean up test files
        for file in ["test_reference.wav", "test_user.wav"]:
            if os.path.exists(file):
                os.remove(file)
    
    return True

def test_data_persistence():
    """Test data persistence functionality"""
    print("💾 Testing Data Persistence...")
    
    test_db = "test_persistence.db"
    auth_system = AuthSystem(test_db)
    
    try:
        # Register a test user
        auth_system.register_user("persistuser", "persist@example.com", "testpass123")
        success, user_data = auth_system.login_user("persistuser", "testpass123")
        user_id = user_data['user_id']
        
        # Test saving analysis data
        print("  Testing analysis data saving...")
        test_analysis_data = [
            {
                'segment_id': 0,
                'start_time': 0.0,
                'end_time': 5.0,
                'differences': [{'timestamp': 1.0, 'freq_diff': 10.0}],
                'statistics': {'average_deviation_hz': 10.0, 'accuracy_percentage': 90.0}
            }
        ]
        
        test_summary_stats = {
            'total_segments': 1,
            'segments_with_issues': 1,
            'overall_summary': 'Test summary'
        }
        
        success, result = auth_system.save_analysis_data(
            user_id, "test_ref.wav", "test_user.wav", 
            test_analysis_data, test_summary_stats, test_analysis_data
        )
        assert success, f"Failed to save analysis data: {result}"
        print("  ✅ Analysis data saved successfully")
        
        # Test retrieving analysis data
        print("  Testing analysis data retrieval...")
        success, analyses = auth_system.get_user_analyses(user_id, limit=5)
        assert success, f"Failed to retrieve analyses: {analyses}"
        assert len(analyses) > 0, "Should have at least one analysis"
        
        analysis = analyses[0]
        assert 'id' in analysis
        assert 'date' in analysis
        assert 'reference_file' in analysis
        assert 'user_file' in analysis
        assert 'summary_stats' in analysis
        assert 'segments_data' in analysis
        
        print("  ✅ Analysis data retrieved successfully")
        
        # Test retrieving specific analysis
        print("  Testing specific analysis retrieval...")
        success, analysis_data = auth_system.get_analysis_by_id(analysis['id'], user_id)
        assert success, f"Failed to retrieve specific analysis: {analysis_data}"
        assert 'analysis_data' in analysis_data
        assert 'summary_stats' in analysis_data
        assert 'segments_data' in analysis_data
        
        print("  ✅ Specific analysis retrieval successful")
        
        print("✅ Data persistence tests passed!")
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False
    
    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)
    
    return True

def main():
    """Run all tests"""
    print("🧪 Enhanced QIRAT AI System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Authentication System", test_authentication_system),
        ("5-Second Segment Analysis", test_5second_segment_analysis),
        ("Data Persistence", test_data_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced system is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 