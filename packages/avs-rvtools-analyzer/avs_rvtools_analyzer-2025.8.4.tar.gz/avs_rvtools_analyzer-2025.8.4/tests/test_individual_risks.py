#!/usr/bin/env python3
"""
Individual Risk Detection Tests

Tests each risk detection function independently to ensure proper functionality.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

# Import all risk detection functions
from avs_rvtools_analyzer.risk_detection import (
    detect_esx_versions,
    detect_vusb_devices,
    detect_risky_disks,
    detect_non_dvs_switches,
    detect_snapshots,
    detect_suspended_vms,
    detect_oracle_vms,
    detect_dvport_issues,
    detect_non_intel_hosts,
    detect_vmtools_not_running,
    detect_cdrom_issues,
    detect_large_provisioned_vms,
    detect_high_vcpu_vms,
    detect_high_memory_vms,
    detect_hw_version_compatibility,
)


class TestESXVersionRiskDetection:
    """Test ESX version risk detection individually."""

    def test_detect_esx_versions_finds_old_versions(self, comprehensive_excel_data):
        """Test that old ESX versions are detected."""
        result = detect_esx_versions(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect ESX version issues"
        assert 'data' in result
        assert isinstance(result['data'], dict)

        # Should find old versions like 6.5.0 and 6.7.0
        version_data = result['data']
        assert any('6.5.0' in str(version) or '6.7.0' in str(version) for version in version_data.keys())

    def test_detect_esx_versions_structure(self, comprehensive_excel_data):
        """Test the structure of ESX version detection results."""
        result = detect_esx_versions(comprehensive_excel_data)

        assert 'count' in result
        assert 'data' in result
        assert isinstance(result['count'], int)


class TestUSBDeviceRiskDetection:
    """Test USB device risk detection individually."""

    def test_detect_vusb_devices_finds_devices(self, comprehensive_excel_data):
        """Test that USB devices are detected."""
        result = detect_vusb_devices(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect USB devices"
        assert 'data' in result
        assert isinstance(result['data'], list)

        # Check that we have the expected USB devices
        usb_devices = result['data']
        assert len(usb_devices) >= 5, "Should find at least 5 USB devices from test data"

        # Verify structure of USB device data
        for device in usb_devices:
            assert 'VM' in device
            assert 'Device Type' in device
            assert 'Connected' in device

    def test_detect_vusb_devices_vm_names(self, comprehensive_excel_data):
        """Test that specific VMs with USB devices are detected."""
        result = detect_vusb_devices(comprehensive_excel_data)

        vm_names = [device['VM'] for device in result['data']]
        expected_vms = ['vm-web-server-01', 'vm-app-server-01', 'vm-db-oracle-01']

        for vm in expected_vms:
            assert vm in vm_names, f"Should detect USB device on {vm}"


class TestRiskyDiskRiskDetection:
    """Test risky disk risk detection individually."""

    def test_detect_risky_disks_finds_raw_disks(self, comprehensive_excel_data):
        """Test that raw device mapping disks are detected."""
        result = detect_risky_disks(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect risky disks"
        assert 'data' in result

        # Should find raw disks and independent disks
        risky_disks = result['data']
        raw_disks = [disk for disk in risky_disks if str(disk.get('Raw', '')).lower() == 'true']
        independent_disks = [disk for disk in risky_disks if 'independent' in str(disk.get('Disk Mode', '')).lower()]

        assert len(raw_disks) > 0, "Should find raw device mapping disks"
        assert len(independent_disks) > 0, "Should find independent mode disks"


class TestNetworkSwitchRiskDetection:
    """Test network switch risk detection individually."""

    def test_detect_non_dvs_switches_finds_standard_switches(self, comprehensive_excel_data):
        """Test that standard vSwitches are detected."""
        result = detect_non_dvs_switches(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect standard vSwitches"
        assert 'data' in result
        assert isinstance(result['data'], list), "Data should be a list of switch records"

        # Should find switches with detailed information
        switch_data = result['data']

        # Verify structure of switch data
        for switch_record in switch_data:
            assert 'Switch' in switch_record, "Each record should have Switch name"
            assert 'Switch Type' in switch_record, "Each record should have Switch Type"
            assert 'Port Count' in switch_record, "Each record should have Port Count"
            assert switch_record['Switch Type'] in ['Standard', 'Distributed'], "Switch Type should be Standard or Distributed"
            assert isinstance(switch_record['Port Count'], int), "Port Count should be an integer"

        # Should find at least some standard switches
        standard_switches = [switch for switch in switch_data if switch['Switch Type'] == 'Standard']
        assert len(standard_switches) > 0, "Should find at least one standard vSwitch"

        # Check for expected standard switch names (vSwitch0, vSwitch1, vSwitch2 from test data)
        standard_switch_names = [switch['Switch'] for switch in standard_switches]
        expected_standard_switches = ['vSwitch0', 'vSwitch1', 'vSwitch2']

        for expected_switch in expected_standard_switches:
            assert expected_switch in standard_switch_names, f"Should detect {expected_switch} as standard vSwitch"

    def test_detect_non_dvs_switches_only_standard_switches(self):
        """Test detection when there are only standard vSwitches and no distributed switches."""
        # Create test data with only standard vSwitches (no dvSwitch sheet)
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            temp_path = Path(tmp_file.name)

            # Create vNetwork data with only standard vSwitches
            vnetwork_data = pd.DataFrame({
                'VM': [
                    'vm-web-01', 'vm-web-02', 'vm-app-01', 'vm-app-02',
                    'vm-db-01', 'vm-db-02', 'vm-test-01', 'vm-empty-switch'
                ],
                'Network Label': [
                    'VM Network', 'Management Network', 'Storage Network', 'Production Network',
                    'Database Network', 'Backup Network', 'Test Network', 'Disconnected'
                ],
                'Switch': [
                    'vSwitch0', 'vSwitch0', 'vSwitch1', 'vSwitch1',
                    'vSwitch2', 'vSwitch2', 'vSwitch3', ''  # Last one has empty switch
                ],
                'Connected': [True, True, True, True, True, True, True, False],
                'Status': ['Connected'] * 7 + ['Disconnected']
            })

            # Write to Excel file
            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                vnetwork_data.to_excel(writer, sheet_name='vNetwork', index=False)

        try:
            # Load the test data
            excel_data = pd.ExcelFile(temp_path)

            # Test the function
            result = detect_non_dvs_switches(excel_data)

            # Should detect all VMs with non-empty switches as using standard vSwitches
            assert result['count'] == 7, f"Should detect 7 VMs using standard switches (excluding empty switch), got {result['count']}"
            assert 'data' in result
            assert isinstance(result['data'], list)

            switch_data = result['data']

            # All switches should be classified as 'Standard'
            for switch_record in switch_data:
                assert switch_record['Switch Type'] == 'Standard', f"All switches should be Standard, got {switch_record['Switch Type']} for {switch_record['Switch']}"

            # Should find 4 different vSwitches (vSwitch0, vSwitch1, vSwitch2, vSwitch3)
            switch_names = [switch['Switch'] for switch in switch_data]
            expected_switches = ['vSwitch0', 'vSwitch1', 'vSwitch2', 'vSwitch3']

            assert len(switch_names) == 4, f"Should find 4 different switches, got {len(switch_names)}"
            for expected_switch in expected_switches:
                assert expected_switch in switch_names, f"Should find {expected_switch} in results"

            # Verify port counts
            port_counts = {switch['Switch']: switch['Port Count'] for switch in switch_data}
            assert port_counts['vSwitch0'] == 2, "vSwitch0 should have 2 ports"
            assert port_counts['vSwitch1'] == 2, "vSwitch1 should have 2 ports"
            assert port_counts['vSwitch2'] == 2, "vSwitch2 should have 2 ports"
            assert port_counts['vSwitch3'] == 1, "vSwitch3 should have 1 port"

        finally:
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)


class TestSnapshotRiskDetection:
    """Test snapshot risk detection individually."""

    def test_detect_snapshots_finds_snapshots(self, comprehensive_excel_data):
        """Test that VM snapshots are detected."""
        result = detect_snapshots(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect VM snapshots"
        assert 'data' in result
        assert isinstance(result['data'], list)

        # Should find multiple snapshots
        snapshots = result['data']
        assert len(snapshots) >= 8, "Should find at least 8 snapshots from test data"

        # Verify snapshot structure
        for snapshot in snapshots:
            assert 'VM' in snapshot
            assert 'Name' in snapshot
            assert 'Date / time' in snapshot


class TestSuspendedVMRiskDetection:
    """Test suspended VM risk detection individually."""

    def test_detect_suspended_vms_finds_suspended(self, comprehensive_excel_data):
        """Test that suspended VMs are detected."""
        result = detect_suspended_vms(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect suspended VMs"
        assert 'data' in result

        # Should find suspended VMs
        suspended_vms = result['data']
        vm_names = [vm['VM'] for vm in suspended_vms]

        expected_suspended = ['vm-suspended-01', 'vm-suspended-02']
        for vm in expected_suspended:
            assert vm in vm_names, f"Should detect {vm} as suspended"


class TestOracleVMRiskDetection:
    """Test Oracle VM risk detection individually."""

    def test_detect_oracle_vms_finds_oracle(self, comprehensive_excel_data):
        """Test that Oracle VMs are detected."""
        result = detect_oracle_vms(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect Oracle VMs"
        assert 'data' in result

        # Should find Oracle VMs
        oracle_vms = result['data']
        vm_names = [vm['VM'] for vm in oracle_vms]

        expected_oracle = ['vm-db-oracle-01', 'vm-db-oracle-02', 'vm-mixed-issues-01']
        for vm in expected_oracle:
            assert vm in vm_names, f"Should detect {vm} as Oracle VM"


class TestDVPortRiskDetection:
    """Test distributed virtual port risk detection individually."""

    def test_detect_dvport_issues_finds_security_issues(self, comprehensive_excel_data):
        """Test that dvPort security issues are detected."""
        result = detect_dvport_issues(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect dvPort issues"
        assert 'data' in result

        # Should find ports with security issues
        dvport_issues = result['data']

        # Check for specific security issues - handle both string and boolean values
        promiscuous_issues = [issue for issue in dvport_issues if str(issue.get('Allow Promiscuous', '')).lower() == 'true']
        mac_change_issues = [issue for issue in dvport_issues if str(issue.get('Mac Changes', '')).lower() == 'true']
        forged_transmit_issues = [issue for issue in dvport_issues if str(issue.get('Forged Transmits', '')).lower() == 'true']
        ephemeral_issues = [issue for issue in dvport_issues if str(issue.get('Type', '')).lower() == 'ephemeral']

        assert len(promiscuous_issues) > 0, "Should find promiscuous mode issues"
        assert len(mac_change_issues) > 0, "Should find MAC change issues"
        assert len(forged_transmit_issues) > 0, "Should find forged transmit issues"
        assert len(ephemeral_issues) > 0, "Should find ephemeral port type issues"
        
        # Verify that all dvPort results include the Type column
        for issue in dvport_issues:
            assert 'Type' in issue, "All dvPort results should include Type column"


class TestNonIntelHostRiskDetection:
    """Test non-Intel host risk detection individually."""

    def test_detect_non_intel_hosts_finds_amd(self, comprehensive_excel_data):
        """Test that non-Intel hosts are detected."""
        result = detect_non_intel_hosts(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect non-Intel hosts"
        assert 'data' in result

        # Should find AMD hosts
        non_intel_hosts = result['data']
        cpu_models = [host['CPU Model'] for host in non_intel_hosts]

        assert any('AMD' in cpu for cpu in cpu_models), "Should detect AMD hosts"


class TestVMToolsRiskDetection:
    """Test VMware Tools risk detection individually."""

    def test_detect_vmtools_not_running_finds_issues(self, comprehensive_excel_data):
        """Test that VMware Tools issues are detected."""
        result = detect_vmtools_not_running(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect VMware Tools issues"
        assert 'data' in result

        # Should find VMs with tools not running
        vmtools_issues = result['data']

        # All should be powered on with guest state not running
        for issue in vmtools_issues:
            assert issue['Powerstate'] == 'poweredOn'
            assert issue['Guest state'] == 'notRunning'


class TestCDROMRiskDetection:
    """Test CD-ROM device risk detection individually."""

    def test_detect_cdrom_issues_finds_connected_cdroms(self, comprehensive_excel_data):
        """Test that connected CD-ROM devices are detected."""
        result = detect_cdrom_issues(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect connected CD-ROM devices"
        assert 'data' in result

        # Should find VMs with connected CD-ROMs
        cdrom_issues = result['data']

        # All should have Connected = "True" (handle both string and boolean values)
        for issue in cdrom_issues:
            connected_value = str(issue['Connected']).lower()
            assert connected_value == 'true', f"Should only detect VMs with connected CD-ROMs, got: {issue['Connected']}"


class TestLargeProvisionedVMRiskDetection:
    """Test large provisioned VM risk detection individually."""

    def test_detect_large_provisioned_vms_finds_large_vms(self, comprehensive_excel_data):
        """Test that large provisioned VMs are detected."""
        result = detect_large_provisioned_vms(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect large provisioned VMs"
        assert 'data' in result

        # Should find VMs with >10TB provisioned
        large_vms = result['data']

        expected_large_vms = ['vm-large-storage-01', 'vm-large-storage-02', 'vm-mixed-issues-01']
        vm_names = [vm['VM'] for vm in large_vms]

        for vm in expected_large_vms:
            assert vm in vm_names, f"Should detect {vm} as large provisioned VM"


class TestHighVCPURiskDetection:
    """Test high vCPU VM risk detection individually."""

    def test_detect_high_vcpu_vms_finds_high_cpu_vms(self, comprehensive_excel_data):
        """Test that high vCPU VMs are detected."""
        result = detect_high_vcpu_vms(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect high vCPU VMs"
        assert 'data' in result

        # Should find VMs with high CPU counts (72, 64, 80)
        high_vcpu_vms = result['data']

        expected_high_cpu_vms = ['vm-high-cpu-01', 'vm-high-cpu-02', 'vm-mixed-issues-01']
        vm_names = [vm['VM'] for vm in high_vcpu_vms]

        for vm in expected_high_cpu_vms:
            assert vm in vm_names, f"Should detect {vm} as high vCPU VM"


class TestHighMemoryRiskDetection:
    """Test high memory VM risk detection individually."""

    def test_detect_high_memory_vms_finds_high_memory_vms(self, comprehensive_excel_data):
        """Test that high memory VMs are detected."""
        result = detect_high_memory_vms(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect high memory VMs"
        assert 'data' in result

        # Should find VMs with high memory (1TB+)
        high_memory_vms = result['data']

        expected_high_memory_vms = ['vm-high-memory-01', 'vm-high-memory-02', 'vm-mixed-issues-01']
        vm_names = [vm['VM'] for vm in high_memory_vms if 'VM' in vm]

        for vm in expected_high_memory_vms:
            assert vm in vm_names, f"Should detect {vm} as high memory VM"


class TestHWVersionCompatibilityRiskDetection:
    """Test hardware version compatibility risk detection individually."""

    def test_detect_hw_version_compatibility_finds_old_hw(self, comprehensive_excel_data):
        """Test that old hardware versions are detected."""
        result = detect_hw_version_compatibility(comprehensive_excel_data)

        assert result['count'] > 0, "Should detect hardware version compatibility issues"
        assert 'data' in result

        # Should find VMs with old hardware versions (6, 7, 8)
        hw_issues = result['data']

        # Check for specific VMs with old hardware
        vm_names = [vm['VM'] for vm in hw_issues]
        expected_old_hw_vms = ['vm-old-hw-01', 'vm-old-hw-02', 'vm-mixed-issues-01']

        for vm in expected_old_hw_vms:
            assert vm in vm_names, f"Should detect {vm} as having old hardware version"

        # Verify migration method restrictions
        for issue in hw_issues:
            assert 'Unsupported migration methods' in issue
            assert len(issue['Unsupported migration methods']) > 0
