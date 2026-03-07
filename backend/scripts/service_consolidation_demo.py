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
    logger.info("🔍 Service Consolidation Analysis Demo")
    logger.info("=" * 50)
    
    # Initialize the service consolidator
    project_root = Path(__file__).parent.parent.parent
    consolidator = ServiceConsolidator(str(project_root))
    
    logger.info("📁 Project root: {project_root}")
    logger.info()
    
    try:
        # Step 1: Analyze service dependencies
        logger.info("🔍 Step 1: Analyzing service dependencies...")
        dependency_graph = await consolidator.analyze_service_dependencies()
        
        logger.info("✅ Found {len(dependency_graph.nodes)} services")
        logger.info("✅ Identified {len(dependency_graph.edges)} dependencies")
        logger.info("✅ Detected {len(dependency_graph.clusters)} service clusters")
        logger.info()
        
        # Display discovered services
        logger.info("📋 Discovered Services:")
        for service_name, service_info in dependency_graph.nodes.items():
            logger.info("  • {service_name}")
            logger.info("    - Type: {service_info['type']}")
            logger.info("    - Language: {service_info['language']}")
            logger.info("    - Complexity: {service_info['complexity']}/10")
            logger.info("    - Lines of Code: {service_info['lines_of_code']}")
            logger.info("    - Endpoints: {service_info['endpoints']}")
            logger.info("    - Functions: {service_info['functions']}")
        logger.info()
        
        # Display dependencies
        if dependency_graph.edges:
            logger.info("🔗 Service Dependencies:")
            for dep in dependency_graph.edges[:10]:  # Show first 10
                logger.info("  • {dep.source} → {dep.target} ({dep.dependency_type})")
                if dep.critical:
                    logger.info("    ⚠️  Critical dependency")
            if len(dependency_graph.edges) > 10:
                logger.info("  ... and {len(dependency_graph.edges) - 10} more dependencies")
        logger.info()
        
        # Step 2: Identify consolidation candidates
        logger.info("🎯 Step 2: Identifying consolidation candidates...")
        consolidation_plans = consolidator.identify_consolidation_candidates()
        
        logger.info("✅ Generated {len(consolidation_plans)} consolidation plans")
        logger.info()
        
        # Display consolidation plans
        if consolidation_plans:
            logger.info("📋 Consolidation Plans:")
            for i, plan in enumerate(consolidation_plans, 1):
                logger.info("  {i}. {plan.plan_id}")
                logger.info("     Strategy: {plan.strategy.value}")
                logger.info("     Source Services: {', '.join(plan.source_services)}")
                logger.info("     Target Service: {plan.target_service}")
                logger.info("     Estimated Effort: {plan.estimated_effort} hours")
                logger.info("     Risk Level: {plan.risk_level}")
                logger.info("     Benefits:")
                for benefit in plan.benefits[:3]:  # Show first 3 benefits
                    logger.info("       • {benefit}")
                logger.info("     Preserved Functions: {len(plan.preserved_functions)}")
                logger.info()
        
        # Step 3: Generate comprehensive report
        logger.info("📊 Step 3: Generating consolidation report...")
        report = consolidator.generate_consolidation_report()
        
        # Save report to file
        report_file = project_root / "service_consolidation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("✅ Report saved to: {report_file}")
        logger.info()
        
        # Display summary
        logger.info("📈 Consolidation Summary:")
        logger.info("  • Services Analyzed: {report['services_analyzed']}")
        logger.info("  • Dependencies Found: {report['dependencies_found']}")
        logger.info("  • Overlaps Identified: {report['overlaps_identified']}")
        logger.info("  • Consolidation Plans: {report['consolidation_plans']}")
        logger.info()
        
        # Step 4: Demonstrate merge simulation (if plans exist)
        if consolidation_plans:
            logger.info("🔧 Step 4: Demonstrating merge simulation...")
            merger = ServiceMerger(str(project_root))
            
            # Use the first plan for demonstration
            demo_plan = consolidation_plans[0]
            logger.info("📋 Simulating merge for plan: {demo_plan.plan_id}")
            logger.info("   Merging {', '.join(demo_plan.source_services)} → {demo_plan.target_service}")
            
            # Note: This is a simulation - no actual files are modified
            logger.info("⚠️  Note: This is a simulation - no files will be modified")
            
            # Simulate the merge process
            merge_result = await merger.execute_service_merge(demo_plan)
            
            if merge_result.success:
                logger.info("✅ Merge simulation completed successfully!")
                logger.info("   • Merged Service: {merge_result.merged_service}")
                logger.info("   • Original Services: {', '.join(merge_result.original_services)}")
                logger.info("   • Preserved Functions: {len(merge_result.preserved_functions)}")
                logger.info("   • Updated References: {len(merge_result.updated_references)}")
                if merge_result.warnings:
                    logger.info("   • Warnings: {len(merge_result.warnings)}")
            else:
                logger.info("❌ Merge simulation failed:")
                for error in merge_result.errors:
                    logger.info("   • {error}")
            logger.info()
        
        # Step 5: Display recommendations
        logger.info("💡 Recommendations:")
        if consolidation_plans:
            # Find the lowest risk plan
            low_risk_plans = [p for p in consolidation_plans if p.risk_level == 'low']
            if low_risk_plans:
                recommended_plan = min(low_risk_plans, key=lambda p: p.estimated_effort)
                logger.info("  🎯 Recommended: {recommended_plan.plan_id}")
                logger.info("     • Low risk consolidation")
                logger.info("     • Estimated effort: {recommended_plan.estimated_effort} hours")
                logger.info("     • Merges: {', '.join(recommended_plan.source_services)} → {recommended_plan.target_service}")
            else:
                logger.info("  ⚠️  All consolidation plans have medium or high risk")
                logger.info("     Consider starting with smaller, incremental changes")
        else:
            logger.info("  ✅ No immediate consolidation opportunities identified")
            logger.info("     Current architecture appears well-structured")
        
        logger.info()
        logger.info("🎉 Service consolidation analysis complete!")
        logger.info("📄 Full report available at: {report_file}")
        
    except Exception as e:
        logger.error(f"Error during consolidation analysis: {e}")
        logger.info("❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)