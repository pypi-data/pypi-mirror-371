"""
Report generator for differential testing results.

This module generates comprehensive reports in multiple formats
including HTML, JSON, and JUnit XML for test results analysis.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import logging
import xml.etree.ElementTree as ET
from datetime import datetime


class ReportGenerator:
    """
    Generate comprehensive reports for differential testing results.
    
    Supports multiple output formats and provides detailed analysis
    of test execution results and performance metrics.
    """
    
    def __init__(self, test_results: List[Any], output_dir: str, runner_stats: Dict[str, Any] = None):
        """
        Initialize report generator.
        
        Args:
            test_results: List of TestResult objects
            output_dir: Output directory for reports
            runner_stats: Additional runner statistics
        """
        self.test_results = test_results
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.runner_stats = runner_stats or {}
        self.logger = logging.getLogger(__name__)
        
        # Generate timestamp
        self.timestamp = datetime.now()
        
    def generate_json_report(self, output_file: str):
        """Generate JSON report."""
        self.logger.info(f"Generating JSON report: {output_file}")
        
        report_data = {
            'metadata': {
                'generated_at': self.timestamp.isoformat(),
                'framework': 'BICSdifftest',
                'version': '1.0.0'
            },
            'summary': self._generate_summary(),
            'statistics': self.runner_stats,
            'test_results': [self._test_result_to_dict(result) for result in self.test_results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
            
        self.logger.info(f"JSON report saved to {output_file}")
        
    def generate_html_report(self, output_file: str):
        """Generate HTML report."""
        self.logger.info(f"Generating HTML report: {output_file}")
        
        html_content = self._generate_html_content()
        
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        self.logger.info(f"HTML report saved to {output_file}")
        
    def generate_junit_xml(self, output_file: str):
        """Generate JUnit XML report."""
        self.logger.info(f"Generating JUnit XML report: {output_file}")
        
        # Create root testsuite element
        testsuite = ET.Element('testsuite')
        testsuite.set('name', 'BICSdifftest')
        testsuite.set('tests', str(len(self.test_results)))
        testsuite.set('failures', str(self.runner_stats.get('failed_tests', 0)))
        testsuite.set('errors', str(self.runner_stats.get('error_tests', 0)))
        testsuite.set('skipped', str(self.runner_stats.get('skipped_tests', 0)))
        testsuite.set('timestamp', self.timestamp.isoformat())
        
        # Calculate total time
        total_time = sum(result.total_time for result in self.test_results if result.total_time)
        testsuite.set('time', f"{total_time:.3f}")
        
        # Add test cases
        for result in self.test_results:
            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('name', result.test_name)
            testcase.set('classname', result.config_name)
            testcase.set('time', f"{result.total_time:.3f}")
            
            # Add failure/error/skip information
            if result.status.value == 'failed':
                failure = ET.SubElement(testcase, 'failure')
                failure.set('message', result.error_message or 'Test failed')
                failure.text = self._format_error_details(result)
                
            elif result.status.value == 'error':
                error = ET.SubElement(testcase, 'error')
                error.set('message', result.error_message or 'Test error')
                error.text = self._format_error_details(result)
                
            elif result.status.value == 'skipped':
                skipped = ET.SubElement(testcase, 'skipped')
                skipped.set('message', 'Test skipped')
                
        # Write XML
        tree = ET.ElementTree(testsuite)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        self.logger.info(f"JUnit XML report saved to {output_file}")
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary statistics."""
        if not self.test_results:
            return {}
            
        # Basic statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status.value == 'passed')
        failed_tests = sum(1 for r in self.test_results if r.status.value == 'failed')
        error_tests = sum(1 for r in self.test_results if r.status.value == 'error')
        skipped_tests = sum(1 for r in self.test_results if r.status.value == 'skipped')
        
        # Time statistics
        total_time = sum(r.total_time for r in self.test_results if r.total_time)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        compilation_time = sum(r.compilation_time for r in self.test_results if r.compilation_time)
        simulation_time = sum(r.simulation_time for r in self.test_results if r.simulation_time)
        
        # Vector statistics
        total_vectors = sum(r.total_vectors for r in self.test_results if r.total_vectors)
        passed_vectors = sum(r.passed_vectors for r in self.test_results if r.passed_vectors)
        failed_vectors = sum(r.failed_vectors for r in self.test_results if r.failed_vectors)
        
        return {
            'test_counts': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'error': error_tests,
                'skipped': skipped_tests
            },
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'execution_time': {
                'total_time': total_time,
                'average_time': avg_time,
                'compilation_time': compilation_time,
                'simulation_time': simulation_time
            },
            'test_vectors': {
                'total_vectors': total_vectors,
                'passed_vectors': passed_vectors,
                'failed_vectors': failed_vectors,
                'vector_pass_rate': (passed_vectors / total_vectors * 100) if total_vectors > 0 else 0
            }
        }
        
    def _test_result_to_dict(self, result) -> Dict[str, Any]:
        """Convert TestResult to dictionary."""
        result_dict = asdict(result)
        
        # Convert enum to string
        result_dict['status'] = result.status.value
        
        return result_dict
        
    def _format_error_details(self, result) -> str:
        """Format error details for XML output."""
        details = []
        
        if result.error_message:
            details.append(f"Error Message: {result.error_message}")
            
        if result.error_details:
            details.append(f"Error Details: {json.dumps(result.error_details, indent=2)}")
            
        if result.log_file:
            details.append(f"Log File: {result.log_file}")
            
        return '\n'.join(details)
        
    def _generate_html_content(self) -> str:
        """Generate HTML report content."""
        summary = self._generate_summary()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>BICSdifftest Report</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #333;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .summary-card h3 {{
            margin-top: 0;
            color: #333;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .metric:last-child {{
            margin-bottom: 0;
        }}
        .pass-rate {{
            font-size: 24px;
            font-weight: bold;
            color: {('#28a745' if summary.get('pass_rate', 0) >= 80 else '#dc3545' if summary.get('pass_rate', 0) < 50 else '#ffc107')};
        }}
        .test-results {{
            margin-top: 40px;
        }}
        .test-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .test-table th, .test-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .test-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-error {{ color: #fd7e14; font-weight: bold; }}
        .status-skipped {{ color: #6c757d; font-weight: bold; }}
        .expandable {{
            cursor: pointer;
            user-select: none;
        }}
        .error-details {{
            display: none;
            background: #f8d7da;
            padding: 10px;
            margin-top: 5px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
    <script>
        function toggleDetails(id) {{
            var element = document.getElementById(id);
            if (element.style.display === 'none' || element.style.display === '') {{
                element.style.display = 'block';
            }} else {{
                element.style.display = 'none';
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BICSdifftest Report</h1>
            <p>Generated on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Test Results</h3>
                <div class="metric">
                    <span>Total Tests:</span>
                    <span>{summary.get('test_counts', {}).get('total', 0)}</span>
                </div>
                <div class="metric">
                    <span>Passed:</span>
                    <span style="color: #28a745;">{summary.get('test_counts', {}).get('passed', 0)}</span>
                </div>
                <div class="metric">
                    <span>Failed:</span>
                    <span style="color: #dc3545;">{summary.get('test_counts', {}).get('failed', 0)}</span>
                </div>
                <div class="metric">
                    <span>Errors:</span>
                    <span style="color: #fd7e14;">{summary.get('test_counts', {}).get('error', 0)}</span>
                </div>
                <div class="metric">
                    <span>Pass Rate:</span>
                    <span class="pass-rate">{summary.get('pass_rate', 0):.1f}%</span>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>Execution Time</h3>
                <div class="metric">
                    <span>Total Time:</span>
                    <span>{summary.get('execution_time', {}).get('total_time', 0):.2f}s</span>
                </div>
                <div class="metric">
                    <span>Average Time:</span>
                    <span>{summary.get('execution_time', {}).get('average_time', 0):.2f}s</span>
                </div>
                <div class="metric">
                    <span>Compilation Time:</span>
                    <span>{summary.get('execution_time', {}).get('compilation_time', 0):.2f}s</span>
                </div>
                <div class="metric">
                    <span>Simulation Time:</span>
                    <span>{summary.get('execution_time', {}).get('simulation_time', 0):.2f}s</span>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>Test Vectors</h3>
                <div class="metric">
                    <span>Total Vectors:</span>
                    <span>{summary.get('test_vectors', {}).get('total_vectors', 0)}</span>
                </div>
                <div class="metric">
                    <span>Passed Vectors:</span>
                    <span style="color: #28a745;">{summary.get('test_vectors', {}).get('passed_vectors', 0)}</span>
                </div>
                <div class="metric">
                    <span>Failed Vectors:</span>
                    <span style="color: #dc3545;">{summary.get('test_vectors', {}).get('failed_vectors', 0)}</span>
                </div>
                <div class="metric">
                    <span>Vector Pass Rate:</span>
                    <span class="pass-rate">{summary.get('test_vectors', {}).get('vector_pass_rate', 0):.1f}%</span>
                </div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>Test Results</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Total Time (s)</th>
                        <th>Compilation (s)</th>
                        <th>Simulation (s)</th>
                        <th>Vectors</th>
                        <th>Pass Rate</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add test results
        for i, result in enumerate(self.test_results):
            status_class = f"status-{result.status.value}"
            vector_pass_rate = 0
            if result.total_vectors > 0:
                vector_pass_rate = (result.passed_vectors / result.total_vectors) * 100
                
            html += f"""
                    <tr>
                        <td>{result.test_name}</td>
                        <td class="{status_class}">{result.status.value.upper()}</td>
                        <td>{result.total_time:.2f}</td>
                        <td>{result.compilation_time:.2f}</td>
                        <td>{result.simulation_time:.2f}</td>
                        <td>{result.passed_vectors}/{result.total_vectors}</td>
                        <td>{vector_pass_rate:.1f}%</td>
                        <td>
"""
            
            # Add expandable error details if there are errors
            if result.error_message or result.error_details:
                html += f"""
                            <span class="expandable" onclick="toggleDetails('details_{i}')">⯈ Show Details</span>
                            <div id="details_{i}" class="error-details">
                                {self._format_error_for_html(result)}
                            </div>
"""
            else:
                html += "N/A"
                
            html += """
                        </td>
                    </tr>
"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by BICSdifftest Framework</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
        
    def _format_error_for_html(self, result) -> str:
        """Format error information for HTML display."""
        details = []
        
        if result.error_message:
            details.append(f"Error Message: {result.error_message}")
            
        if result.error_details:
            details.append(f"Error Details: {json.dumps(result.error_details, indent=2)}")
            
        if result.log_file:
            details.append(f"Log File: {result.log_file}")
            
        if result.wave_file:
            details.append(f"Wave File: {result.wave_file}")
            
        return '\n'.join(details)