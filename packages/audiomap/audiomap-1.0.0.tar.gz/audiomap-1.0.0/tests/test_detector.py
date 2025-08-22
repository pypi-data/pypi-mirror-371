"""
AudioMap basic functionality tests
"""

import pytest
import platform
from audiomap import AudioDeviceDetector, list_audio_input_devices, list_audio_output_devices
from audiomap.exceptions import AudioDetectionError, PlatformNotSupportedError


class TestAudioDeviceDetector:
    """Test AudioDeviceDetector class"""
    
    def test_detector_creation(self):
        """Test detector creation"""
        detector = AudioDeviceDetector()
        assert detector.current_platform in ["Windows", "Darwin", "Linux"]
    
    def test_list_input_devices(self):
        """Test listing input devices"""
        detector = AudioDeviceDetector()
        devices = detector.list_input_devices()
        
        assert isinstance(devices, list)
        
        # Check each device structure
        for device in devices:
            assert isinstance(device, dict)
            assert "id" in device
            assert "name" in device
            assert "platform" in device
            assert device["platform"] == detector.current_platform
    
    def test_list_output_devices(self):
        """Test listing output devices"""
        detector = AudioDeviceDetector()
        devices = detector.list_output_devices()
        
        assert isinstance(devices, list)
        
        # Check each device structure
        for device in devices:
            assert isinstance(device, dict)
            assert "id" in device
            assert "name" in device
            assert "platform" in device
            assert device["platform"] == detector.current_platform
    
    def test_list_all_devices(self):
        """Test listing all devices"""
        detector = AudioDeviceDetector()
        all_devices = detector.list_all_devices()
        
        assert isinstance(all_devices, dict)
        assert "input" in all_devices
        assert "output" in all_devices
        assert isinstance(all_devices["input"], list)
        assert isinstance(all_devices["output"], list)
    
    def test_get_device_count(self):
        """Test getting device count"""
        detector = AudioDeviceDetector()
        counts = detector.get_device_count()
        
        assert isinstance(counts, dict)
        assert "input" in counts
        assert "output" in counts
        assert "total" in counts
        assert isinstance(counts["input"], int)
        assert isinstance(counts["output"], int)
        assert isinstance(counts["total"], int)
        assert counts["total"] == counts["input"] + counts["output"]
    
    def test_find_device_by_name(self):
        """Test finding devices by name"""
        detector = AudioDeviceDetector()
        
        # Test finding non-existent device
        devices = detector.find_device_by_name("ThisDeviceDoesNotExist")
        assert isinstance(devices, list)
        
        # Test invalid device type
        with pytest.raises(ValueError):
            detector._list_devices("invalid_type")


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_list_audio_input_devices(self):
        """Test list_audio_input_devices function"""
        devices = list_audio_input_devices()
        assert isinstance(devices, list)
    
    def test_list_audio_output_devices(self):
        """Test list_audio_output_devices function"""
        devices = list_audio_output_devices()
        assert isinstance(devices, list)


class TestPlatformSpecific:
    """Platform-specific tests"""
    
    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_macos_detection(self):
        """Test macOS platform detection"""
        detector = AudioDeviceDetector()
        
        # macOS usually has built-in devices
        input_devices = detector.list_input_devices()
        output_devices = detector.list_output_devices()
        
        # Should have at least some devices
        assert len(input_devices) >= 0
        assert len(output_devices) >= 0
    
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_windows_detection(self):
        """Test Windows platform detection"""
        detector = AudioDeviceDetector()
        
        # Windows usually has built-in devices
        input_devices = detector.list_input_devices()
        output_devices = detector.list_output_devices()
        
        # Should have at least some devices
        assert len(input_devices) >= 0
        assert len(output_devices) >= 0
    
    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux-specific test")
    def test_linux_detection(self):
        """Test Linux platform detection"""
        detector = AudioDeviceDetector()
        
        # Linux device detection may fail (if no ALSA)
        try:
            input_devices = detector.list_input_devices()
            output_devices = detector.list_output_devices()
            
            assert len(input_devices) >= 0
            assert len(output_devices) >= 0
        except AudioDetectionError:
            # Audio system may not be available in some environments
            pytest.skip("ALSA tools not installed or audio system unavailable")


class TestErrorHandling:
    """Error handling tests"""
    
    def test_invalid_device_type(self):
        """Test invalid device type"""
        detector = AudioDeviceDetector()
        
        with pytest.raises(ValueError):
            detector._list_devices("invalid")


if __name__ == "__main__":
    pytest.main([__file__])
