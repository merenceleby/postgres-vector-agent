import json
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyze PostgreSQL query execution plans"""
    
    def __init__(self):
        self.scan_types = {
            'Seq Scan': 'sequential',
            'Index Scan': 'index',
            'Index Only Scan': 'index_only',
            'Bitmap Heap Scan': 'bitmap'
        }
    
    def analyze_plan(self, explain_output: Dict) -> Dict:
        """
        Analyze EXPLAIN ANALYZE output
        
        Args:
            explain_output: JSON output from EXPLAIN ANALYZE
            
        Returns:
            Analysis results with optimization recommendations
        """
        if not explain_output or 'Plan' not in explain_output:
            return {'error': 'Invalid EXPLAIN output'}
        
        plan = explain_output['Plan']
        execution_time = explain_output.get('Execution Time', 0)
        planning_time = explain_output.get('Planning Time', 0)
        
        # Extract scan information
        scan_info = self._extract_scan_info(plan)
        
        # Detect performance issues
        issues = self._detect_issues(plan, scan_info, execution_time)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, scan_info)
        
        analysis = {
            'execution_time_ms': execution_time,
            'planning_time_ms': planning_time,
            'total_time_ms': execution_time + planning_time,
            'scan_type': scan_info['primary_scan'],
            'index_used': scan_info['index_used'],
            'rows_scanned': scan_info['rows_scanned'],
            'rows_returned': plan.get('Actual Rows', 0),
            'issues': issues,
            'recommendations': recommendations,
            'raw_plan': plan
        }
        
        return analysis
    
    def _extract_scan_info(self, plan: Dict, level: int = 0) -> Dict:
        """Extract scan information from query plan"""
        info = {
            'primary_scan': 'unknown',
            'index_used': False,
            'index_name': None,
            'rows_scanned': 0,
            'scans_found': []
        }
        
        node_type = plan.get('Node Type', '')
        
        # Check if this is a scan node
        if 'Scan' in node_type:
            info['scans_found'].append(node_type)
            if level == 0 or not info['primary_scan']:
                info['primary_scan'] = self.scan_types.get(node_type, 'unknown')
            
            if 'Index' in node_type:
                info['index_used'] = True
                info['index_name'] = plan.get('Index Name')
            
            info['rows_scanned'] += plan.get('Actual Rows', 0)
        
        # Recursively check child plans
        if 'Plans' in plan:
            for child_plan in plan['Plans']:
                child_info = self._extract_scan_info(child_plan, level + 1)
                if not info['index_used'] and child_info['index_used']:
                    info['index_used'] = child_info['index_used']
                    info['index_name'] = child_info['index_name']
                info['rows_scanned'] += child_info['rows_scanned']
                info['scans_found'].extend(child_info['scans_found'])
        
        return info
    
    def _detect_issues(self, plan: Dict, scan_info: Dict, execution_time: float) -> List[str]:
        """Detect performance issues"""
        issues = []
        
        # Issue 1: Sequential scan on large dataset
        if scan_info['primary_scan'] == 'sequential':
            if scan_info['rows_scanned'] > 1000:
                issues.append('SEQUENTIAL_SCAN_LARGE_DATASET')
            else:
                issues.append('SEQUENTIAL_SCAN_SMALL_DATASET')
        
        # Issue 2: High execution time
        if execution_time > 100:
            issues.append('HIGH_EXECUTION_TIME')
        
        # Issue 3: No index used
        if not scan_info['index_used'] and scan_info['rows_scanned'] > 500:
            issues.append('NO_INDEX_AVAILABLE')
        
        # Issue 4: High rows scanned vs returned ratio
        rows_returned = plan.get('Actual Rows', 0)
        if scan_info['rows_scanned'] > 0:
            selectivity = rows_returned / scan_info['rows_scanned']
            if selectivity < 0.1 and scan_info['rows_scanned'] > 1000:
                issues.append('LOW_SELECTIVITY')
        
        return issues
    
    def _generate_recommendations(self, issues: List[str], scan_info: Dict) -> List[Dict]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if 'SEQUENTIAL_SCAN_LARGE_DATASET' in issues:
            recommendations.append({
                'type': 'CREATE_INDEX',
                'priority': 'HIGH',
                'action': 'create_hnsw_index',
                'reasoning': f'Sequential scan detected on {scan_info["rows_scanned"]} rows. '
                           'Vector similarity search requires an index for acceptable performance.',
                'expected_improvement': '10-100x faster queries'
            })
        
        if 'HIGH_EXECUTION_TIME' in issues and not scan_info['index_used']:
            recommendations.append({
                'type': 'CREATE_INDEX',
                'priority': 'HIGH',
                'action': 'create_hnsw_index',
                'reasoning': 'High execution time without index usage. HNSW index recommended.',
                'expected_improvement': '40-50x faster queries'
            })
        
        if 'NO_INDEX_AVAILABLE' in issues:
            recommendations.append({
                'type': 'CREATE_INDEX',
                'priority': 'MEDIUM',
                'action': 'create_ivfflat_index',
                'reasoning': 'No vector index found. Consider IVFFlat for larger datasets.',
                'expected_improvement': '20-30x faster queries'
            })
        
        if 'LOW_SELECTIVITY' in issues:
            recommendations.append({
                'type': 'OPTIMIZE_QUERY',
                'priority': 'MEDIUM',
                'action': 'add_filters',
                'reasoning': 'Low selectivity detected. Consider adding WHERE clauses.',
                'expected_improvement': 'Reduced rows scanned'
            })
        
        return recommendations
    
    def format_analysis(self, analysis: Dict) -> str:
        """Format analysis results for display"""
        output = []
        output.append("=" * 60)
        output.append("QUERY PERFORMANCE ANALYSIS")
        output.append("=" * 60)
        output.append(f"Execution Time: {analysis['execution_time_ms']:.2f} ms")
        output.append(f"Planning Time: {analysis['planning_time_ms']:.2f} ms")
        output.append(f"Total Time: {analysis['total_time_ms']:.2f} ms")
        output.append(f"Scan Type: {analysis['scan_type']}")
        output.append(f"Index Used: {analysis['index_used']}")
        output.append(f"Rows Scanned: {analysis['rows_scanned']}")
        output.append(f"Rows Returned: {analysis['rows_returned']}")
        
        if analysis['issues']:
            output.append("\n⚠️  ISSUES DETECTED:")
            for issue in analysis['issues']:
                output.append(f"  - {issue}")
        
        if analysis['recommendations']:
            output.append("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                output.append(f"\n{i}. {rec['type']} (Priority: {rec['priority']})")
                output.append(f"   Action: {rec['action']}")
                output.append(f"   Reasoning: {rec['reasoning']}")
                output.append(f"   Expected: {rec['expected_improvement']}")
        
        output.append("=" * 60)
        
        return "\n".join(output)