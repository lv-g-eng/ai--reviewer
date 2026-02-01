#!/usr/bin/env python3
"""
Service Consolidation Demo Script

This script demonstrates the service consolidation analysis and planning
functionality by analyzing the current microservices architecture and
generating consolidation recommendations.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the backend app to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.service_consolidator import ServiceConsolidator
from app.services.service_merger import ServiceMerger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main demo function"""
    print("🔍 Service Consolidation Analysis Demo")
    print("=" * 50)
    
    # Initialize the service consolidator
    project_root = Path(__file__).parent.parent.parent
    consolidator = ServiceConsolidator(str(project_root))
    
    print(f"📁 Project root: {project_root}")
    print()
    
    try:
        # Step 1: Analyze service dependencies
        print("🔍 Step 1: Analyzing service dependencies...")
        dependency_graph = await consolidator.analyze_service_dependencies()
        
        print(f"✅ Found {len(dependency_graph.nodes)} services")
        print(f"✅ Identified {len(dependency_graph.edges)} dependencies")
        print(f"✅ Detected {len(dependency_graph.clusters)} service clusters")
        print()
        
        # Display discovered services
        print("📋 Discovered Services:")
        for service_name, service_info in dependency_graph.nodes.items():
            print(f"  • {service_name}")
            print(f"    - Type: {service_info['type']}")
            print(f"    - Language: {service_info['language']}")
            print(f"    - Complexity: {service_info['complexity']}/10")
            print(f"    - Lines of Code: {service_info['lines_of_code']}")
            print(f"    - Endpoints: {service_info['endpoints']}")
            print(f"    - Functions: {service_info['functions']}")
        print()
        
        # Display dependencies
        if dependency_graph.edges:
            print("🔗 Service Dependencies:")
            for dep in dependency_graph.edges[:10]:  # Show first 10
                print(f"  • {dep.source} → {dep.target} ({dep.dependency_type})")
                if dep.critical:
                    print("    ⚠️  Critical dependency")
            if len(dependency_graph.edges) > 10:
                print(f"  ... and {len(dependency_graph.edges) - 10} more dependencies")
        print()
        
        # Step 2: Identify consolidation candidates
        print("🎯 Step 2: Identifying consolidation candidates...")
        consolidation_plans = consolidator.identify_consolidation_candidates()
        
        print(f"✅ Generated {len(consolidation_plans)} consolidation plans")
        print()
        
        # Display consolidation plans
        if consolidation_plans:
            print("📋 Consolidation Plans:")
            for i, plan in enumerate(consolidation_plans, 1):
                print(f"  {i}. {plan.plan_id}")
                print(f"     Strategy: {plan.strategy.value}")
                print(f"     Source Services: {', '.join(plan.source_services)}")
                print(f"     Target Service: {plan.target_service}")
                print(f"     Estimated Effort: {plan.estimated_effort} hours")
                print(f"     Risk Level: {plan.risk_level}")
                print(f"     Benefits:")
                for benefit in plan.benefits[:3]:  # Show first 3 benefits
                    print(f"       • {benefit}")
                print(f"     Preserved Functions: {len(plan.preserved_functions)}")
                print()
        
        # Step 3: Generate comprehensive report
        print("📊 Step 3: Generating consolidation report...")
        report = consolidator.generate_consolidation_report()
        
        # Save report to file
        report_file = project_root / "service_consolidation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to: {report_file}")
        print()
        
        # Display summary
        print("📈 Consolidation Summary:")
        print(f"  • Services Analyzed: {report['services_analyzed']}")
        print(f"  • Dependencies Found: {report['dependencies_found']}")
        print(f"  • Overlaps Identified: {report['overlaps_identified']}")
        print(f"  • Consolidation Plans: {report['consolidation_plans']}")
        print()
        
        # Step 4: Demonstrate merge simulation (if plans exist)
        if consolidation_plans:
            print("🔧 Step 4: Demonstrating merge simulation...")
            merger = ServiceMerger(str(project_root))
            
            # Use the first plan for demonstration
            demo_plan = consolidation_plans[0]
            print(f"📋 Simulating merge for plan: {demo_plan.plan_id}")
            print(f"   Merging {', '.join(demo_plan.source_services)} → {demo_plan.target_service}")
            
            # Note: This is a simulation - no actual files are modified
            print("⚠️  Note: This is a simulation - no files will be modified")
            
            # Simulate the merge process
            merge_result = await merger.execute_service_merge(demo_plan)
            
            if merge_result.success:
                print("✅ Merge simulation completed successfully!")
                print(f"   • Merged Service: {merge_result.merged_service}")
                print(f"   • Original Services: {', '.join(merge_result.original_services)}")
                print(f"   • Preserved Functions: {len(merge_result.preserved_functions)}")
                print(f"   • Updated References: {len(merge_result.updated_references)}")
                if merge_result.warnings:
                    print(f"   • Warnings: {len(merge_result.warnings)}")
            else:
                print("❌ Merge simulation failed:")
                for error in merge_result.errors:
                    print(f"   • {error}")
            print()
        
        # Step 5: Display recommendations
        print("💡 Recommendations:")
        if consolidation_plans:
            # Find the lowest risk plan
            low_risk_plans = [p for p in consolidation_plans if p.risk_level == 'low']
            if low_risk_plans:
                recommended_plan = min(low_risk_plans, key=lambda p: p.estimated_effort)
                print(f"  🎯 Recommended: {recommended_plan.plan_id}")
                print(f"     • Low risk consolidation")
                print(f"     • Estimated effort: {recommended_plan.estimated_effort} hours")
                print(f"     • Merges: {', '.join(recommended_plan.source_services)} → {recommended_plan.target_service}")
            else:
                print("  ⚠️  All consolidation plans have medium or high risk")
                print("     Consider starting with smaller, incremental changes")
        else:
            print("  ✅ No immediate consolidation opportunities identified")
            print("     Current architecture appears well-structured")
        
        print()
        print("🎉 Service consolidation analysis complete!")
        print(f"📄 Full report available at: {report_file}")
        
    except Exception as e:
        logger.error(f"Error during consolidation analysis: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)