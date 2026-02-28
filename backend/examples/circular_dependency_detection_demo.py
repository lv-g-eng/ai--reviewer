"""
Circular Dependency Detection Demo

This script demonstrates how to use the CircularDependencyDetector
to find and analyze circular dependencies in code dependency graphs.

Usage:
    python examples/circular_dependency_detection_demo.py
"""
import asyncio
from app.services.graph_builder import (
    CircularDependencyDetector,
    CycleSeverity
)


async def demo_basic_detection():
    """Demonstrate basic cycle detection"""
    print("=" * 60)
    print("Demo 1: Basic Cycle Detection")
    print("=" * 60)
    
    detector = CircularDependencyDetector()
    
    # Detect all cycles in the graph
    result = await detector.detect_cycles()
    
    print(f"\n📊 Detection Results:")
    print(f"   Total cycles found: {result.total_cycles}")
    print(f"   Detection time: {result.detection_time_ms:.2f}ms")
    print(f"   Affected files: {len(result.affected_files)}")
    
    # Show severity breakdown
    print(f"\n📈 Severity Breakdown:")
    for severity, count in result.severity_breakdown.items():
        emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }.get(severity, "⚪")
        print(f"   {emoji} {severity.upper()}: {count} cycles")
    
    # List cycles
    if result.cycles:
        print(f"\n🔄 Detected Cycles:")
        for i, cycle in enumerate(result.cycles[:5], 1):  # Show first 5
            print(f"\n   Cycle {i}: {cycle.cycle_id}")
            print(f"   ├─ Severity: {cycle.severity.value}")
            print(f"   ├─ Depth: {cycle.depth} nodes")
            print(f"   ├─ Complexity: {cycle.total_complexity} (avg: {cycle.avg_complexity})")
            print(f"   └─ Path: {' → '.join(cycle.nodes[:4])}" + 
                  (" → ..." if len(cycle.nodes) > 4 else ""))
        
        if len(result.cycles) > 5:
            print(f"\n   ... and {len(result.cycles) - 5} more cycles")
    else:
        print("\n✅ No circular dependencies found!")


async def demo_severity_filtering():
    """Demonstrate filtering by severity"""
    print("\n\n" + "=" * 60)
    print("Demo 2: Severity Filtering")
    print("=" * 60)
    
    detector = CircularDependencyDetector()
    
    # Only detect high and critical severity cycles
    result = await detector.detect_cycles(min_severity=CycleSeverity.HIGH)
    
    print(f"\n🔍 High/Critical Severity Cycles:")
    print(f"   Found: {result.total_cycles} cycles")
    
    for cycle in result.cycles:
        severity_emoji = "🔴" if cycle.severity == CycleSeverity.CRITICAL else "🟠"
        print(f"\n   {severity_emoji} {cycle.cycle_id}")
        print(f"      Severity: {cycle.severity.value}")
        print(f"      Nodes: {', '.join(cycle.nodes[:3])}" + 
              (f" + {len(cycle.nodes) - 3} more" if len(cycle.nodes) > 3 else ""))


async def demo_entity_specific_detection():
    """Demonstrate detecting cycles for a specific entity"""
    print("\n\n" + "=" * 60)
    print("Demo 3: Entity-Specific Detection")
    print("=" * 60)
    
    detector = CircularDependencyDetector()
    
    # Example: Check if a specific entity is involved in cycles
    entity_name = "UserService"
    file_path = "/src/services/user_service.py"
    
    print(f"\n🔎 Checking cycles for: {entity_name}")
    
    cycles = await detector.detect_cycles_for_entity(
        entity_name=entity_name,
        file_path=file_path
    )
    
    if cycles:
        print(f"   ⚠️  Found {len(cycles)} cycles involving {entity_name}:")
        for cycle in cycles:
            print(f"\n   • {cycle.cycle_id}")
            print(f"     Severity: {cycle.severity.value}")
            print(f"     Other nodes: {', '.join([n for n in cycle.nodes if n != entity_name][:3])}")
    else:
        print(f"   ✅ No cycles found for {entity_name}")


async def demo_visualization_data():
    """Demonstrate getting visualization data"""
    print("\n\n" + "=" * 60)
    print("Demo 4: Visualization Data Generation")
    print("=" * 60)
    
    detector = CircularDependencyDetector()
    
    # First, detect cycles
    result = await detector.detect_cycles()
    
    if result.cycles:
        # Get visualization data for the first cycle
        cycle = result.cycles[0]
        print(f"\n📊 Generating visualization data for: {cycle.cycle_id}")
        
        viz_data = await detector.get_cycle_visualization_data(cycle.cycle_id)
        
        if viz_data:
            print(f"\n   Visualization Data:")
            print(f"   ├─ Nodes: {len(viz_data['nodes'])}")
            print(f"   ├─ Edges: {len(viz_data['edges'])}")
            print(f"   ├─ Severity: {viz_data['severity']}")
            print(f"   └─ Metadata:")
            for key, value in viz_data['metadata'].items():
                print(f"      • {key}: {value}")
            
            print(f"\n   Node Details:")
            for node in viz_data['nodes'][:3]:
                print(f"   • {node['label']} ({node['file_path']})")
            
            print(f"\n   Edge Details:")
            for edge in viz_data['edges'][:3]:
                print(f"   • {edge['source']} → {edge['target']}")
        else:
            print("   ❌ Could not generate visualization data")
    else:
        print("\n   ℹ️  No cycles to visualize")


async def demo_severity_calculation():
    """Demonstrate severity calculation logic"""
    print("\n\n" + "=" * 60)
    print("Demo 5: Severity Calculation Examples")
    print("=" * 60)
    
    detector = CircularDependencyDetector()
    
    test_cases = [
        (2, 10, 5.0, "Small cycle, low complexity"),
        (5, 60, 12.0, "Medium cycle, moderate complexity"),
        (8, 120, 15.0, "Large cycle, high complexity"),
        (15, 300, 20.0, "Very large cycle, critical complexity")
    ]
    
    print("\n   Severity Calculation Examples:")
    for depth, total_complexity, avg_complexity, description in test_cases:
        severity = detector._calculate_severity(depth, total_complexity, avg_complexity)
        
        emoji = {
            CycleSeverity.LOW: "🟢",
            CycleSeverity.MEDIUM: "🟡",
            CycleSeverity.HIGH: "🟠",
            CycleSeverity.CRITICAL: "🔴"
        }[severity]
        
        print(f"\n   {emoji} {severity.value.upper()}")
        print(f"      {description}")
        print(f"      Depth: {depth}, Total Complexity: {total_complexity}, Avg: {avg_complexity}")


async def demo_json_serialization():
    """Demonstrate JSON serialization"""
    print("\n\n" + "=" * 60)
    print("Demo 6: JSON Serialization")
    print("=" * 60)
    
    detector = CircularDependencyDetector()
    result = await detector.detect_cycles()
    
    # Convert to dictionary (JSON-serializable)
    result_dict = result.to_dict()
    
    print("\n   Serialized Result Structure:")
    print(f"   ├─ total_cycles: {result_dict['total_cycles']}")
    print(f"   ├─ detection_time_ms: {result_dict['detection_time_ms']}")
    print(f"   ├─ severity_breakdown: {result_dict['severity_breakdown']}")
    print(f"   ├─ affected_files: {len(result_dict['affected_files'])} files")
    print(f"   └─ cycles: {len(result_dict['cycles'])} cycle objects")
    
    if result_dict['cycles']:
        print("\n   First Cycle Structure:")
        cycle = result_dict['cycles'][0]
        for key, value in cycle.items():
            if isinstance(value, list) and len(value) > 3:
                print(f"   ├─ {key}: [{len(value)} items]")
            else:
                print(f"   ├─ {key}: {value}")


async def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("Circular Dependency Detection Demo")
    print("=" * 60)
    print("\nThis demo shows how to use the CircularDependencyDetector")
    print("to find and analyze circular dependencies in code graphs.")
    
    try:
        await demo_basic_detection()
        await demo_severity_filtering()
        await demo_entity_specific_detection()
        await demo_visualization_data()
        await demo_severity_calculation()
        await demo_json_serialization()
        
        print("\n\n" + "=" * 60)
        print("Demo Complete!")
        print("=" * 60)
        print("\n✅ All demos executed successfully")
        print("\nFor more information, see:")
        print("  • backend/app/services/graph_builder/CIRCULAR_DEPENDENCY_DETECTOR_README.md")
        print("  • backend/tests/test_circular_dependency_detector.py")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {str(e)}")
        print("\nNote: This demo requires a running Neo4j instance with data.")
        print("To run with real data:")
        print("  1. Start Neo4j database")
        print("  2. Build a dependency graph using GraphBuilderService")
        print("  3. Run this demo")


if __name__ == "__main__":
    asyncio.run(main())
