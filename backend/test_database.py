"""
DATABASE TEST SCRIPT
====================
Purpose: Test database functionality

Run this to verify database is working correctly.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db, get_database_info
from app.models import Complaint, InputType, ComplaintStatus


def test_database_connection():
    """Test 1: Database connection"""
    print("\n" + "=" * 70)
    print("TEST 1: DATABASE CONNECTION")
    print("=" * 70)
    
    try:
        # Get database info
        info = get_database_info()
        print(f"✅ Database Type: {info['type']}")
        print(f"✅ Database Location: {info['url']}")
        print(f"✅ Status: {info['status']}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_table_creation():
    """Test 2: Table creation"""
    print("\n" + "=" * 70)
    print("TEST 2: TABLE CREATION")
    print("=" * 70)
    
    try:
        # Initialize database (creates tables)
        init_db()
        print("✅ Tables created successfully")
        
        # Show table structure
        print("\nTable: complaints")
        print("Columns:")
        for column in Complaint.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False


def test_insert_complaint():
    """Test 3: Insert complaint"""
    print("\n" + "=" * 70)
    print("TEST 3: INSERT COMPLAINT")
    print("=" * 70)
    
    try:
        db = SessionLocal()
        
        # Create test complaint
        complaint = Complaint(
            complaint_text="Test complaint: Hot water not available",
            input_type=InputType.TEXT,
            predicted_category="Hostel",
            confidence_score=0.87,
            status=ComplaintStatus.AUTO_ROUTED,
            department="Hostel",
            student_id="TEST001"
        )
        
        # Add to database
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        
        print(f"✅ Complaint inserted successfully")
        print(f"   ID: {complaint.id}")
        print(f"   Text: {complaint.complaint_text}")
        print(f"   Category: {complaint.predicted_category}")
        print(f"   Confidence: {complaint.confidence_score:.0%}")
        print(f"   Status: {complaint.status.value}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        return False


def test_query_complaints():
    """Test 4: Query complaints"""
    print("\n" + "=" * 70)
    print("TEST 4: QUERY COMPLAINTS")
    print("=" * 70)
    
    try:
        db = SessionLocal()
        
        # Query all complaints
        complaints = db.query(Complaint).all()
        print(f"✅ Found {len(complaints)} complaint(s)")
        
        # Show each complaint
        for complaint in complaints:
            print(f"\n   Complaint #{complaint.id}:")
            print(f"   - Text: {complaint.complaint_text[:50]}...")
            print(f"   - Category: {complaint.predicted_category}")
            print(f"   - Confidence: {complaint.confidence_score:.0%}")
            print(f"   - Status: {complaint.status.value}")
            print(f"   - Created: {complaint.created_at}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False


def test_filter_complaints():
    """Test 5: Filter complaints"""
    print("\n" + "=" * 70)
    print("TEST 5: FILTER COMPLAINTS")
    print("=" * 70)
    
    try:
        db = SessionLocal()
        
        # Filter by category
        hostel_complaints = db.query(Complaint).filter(
            Complaint.predicted_category == "Hostel"
        ).all()
        print(f"✅ Hostel complaints: {len(hostel_complaints)}")
        
        # Filter by status
        auto_routed = db.query(Complaint).filter(
            Complaint.status == ComplaintStatus.AUTO_ROUTED
        ).all()
        print(f"✅ Auto-routed complaints: {len(auto_routed)}")
        
        # Filter by confidence
        high_confidence = db.query(Complaint).filter(
            Complaint.confidence_score >= 0.8
        ).all()
        print(f"✅ High confidence (>=80%): {len(high_confidence)}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Filter failed: {e}")
        return False


def test_update_complaint():
    """Test 6: Update complaint"""
    print("\n" + "=" * 70)
    print("TEST 6: UPDATE COMPLAINT")
    print("=" * 70)
    
    try:
        db = SessionLocal()
        
        # Get first complaint
        complaint = db.query(Complaint).first()
        
        if not complaint:
            print("⚠️ No complaints to update")
            db.close()
            return True
        
        # Update status
        old_status = complaint.status.value
        complaint.status = ComplaintStatus.IN_PROGRESS
        complaint.notes = "Test update: Status changed"
        
        db.commit()
        db.refresh(complaint)
        
        print(f"✅ Complaint #{complaint.id} updated")
        print(f"   Old status: {old_status}")
        print(f"   New status: {complaint.status.value}")
        print(f"   Notes: {complaint.notes}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Update failed: {e}")
        return False


def test_statistics():
    """Test 7: Statistics"""
    print("\n" + "=" * 70)
    print("TEST 7: STATISTICS")
    print("=" * 70)
    
    try:
        from sqlalchemy import func
        db = SessionLocal()
        
        # Total complaints
        total = db.query(func.count(Complaint.id)).scalar()
        print(f"✅ Total complaints: {total}")
        
        # By category
        by_category = db.query(
            Complaint.predicted_category,
            func.count(Complaint.id)
        ).group_by(Complaint.predicted_category).all()
        
        print("\n   By Category:")
        for category, count in by_category:
            print(f"   - {category}: {count}")
        
        # Average confidence
        avg_confidence = db.query(func.avg(Complaint.confidence_score)).scalar()
        print(f"\n   Average Confidence: {avg_confidence:.0%}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CAMPUSAID - DATABASE TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Creation", test_table_creation),
        ("Insert Complaint", test_insert_complaint),
        ("Query Complaints", test_query_complaints),
        ("Filter Complaints", test_filter_complaints),
        ("Update Complaint", test_update_complaint),
        ("Statistics", test_statistics)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print("=" * 70)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nDatabase is working correctly!")
        print("\nNext steps:")
        print("1. Start the server: python -m uvicorn app.main:app --reload")
        print("2. Test API endpoints")
        print("3. Check database file: campusaid.db")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Please check the errors above.")
    
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
