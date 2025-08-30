"""
Timeline Generator for NewsNeuron
Creates entity timelines and story evolution visualizations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

from app.services.hybrid_retriever import HybridRetriever


class TimelineGenerator:
    """
    Generates timeline visualizations for entities and story evolution
    """
    
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
    
    async def generate_timeline(
        self,
        entity_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Generate timeline for a specific entity
        
        Args:
            entity_name: Name of the entity to track
            start_date: Optional start date for timeline
            end_date: Optional end date for timeline
            limit: Maximum number of timeline events
        
        Returns:
            Dictionary with timeline events and metadata
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # Default to 1 year
            
            # Get entity timeline from knowledge graph
            timeline_events = await self._get_entity_timeline_events(
                entity_name=entity_name,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Enrich events with additional context
            enriched_events = await self._enrich_timeline_events(timeline_events)
            
            # Sort events by date
            enriched_events.sort(key=lambda x: x.get("date", datetime.min), reverse=True)
            
            return {
                "events": enriched_events,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "entity_name": entity_name,
                "total_events": len(enriched_events)
            }
            
        except Exception as e:
            print(f"Error generating timeline: {str(e)}")
            return {
                "events": [],
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "entity_name": entity_name,
                "total_events": 0
            }
    
    async def _get_entity_timeline_events(
        self,
        entity_name: str,
        start_date: datetime,
        end_date: datetime,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Get timeline events for entity from Neo4j
        """
        try:
            # Get timeline from Neo4j
            neo4j_timeline = await self.retriever.neo4j_client.get_entity_timeline(
                entity_name=entity_name,
                limit=limit
            )
            
            # Convert to timeline events format
            events = []
            for event in neo4j_timeline:
                # Parse date
                try:
                    if event.get("published_date"):
                        event_date = datetime.fromisoformat(
                            event["published_date"].replace('Z', '+00:00')
                        )
                        
                        # Filter by date range
                        if start_date <= event_date <= end_date:
                            events.append({
                                "id": event.get("supabase_id"),
                                "title": event.get("title", ""),
                                "date": event_date,
                                "source": event.get("source"),
                                "supabase_id": event.get("supabase_id")
                            })
                except Exception as date_error:
                    print(f"Error parsing date: {date_error}")
                    continue
            
            return events
            
        except Exception as e:
            print(f"Error getting entity timeline events: {str(e)}")
            return []
    
    async def _enrich_timeline_events(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich timeline events with additional context from Supabase
        """
        enriched_events = []
        
        for event in events:
            try:
                supabase_id = event.get("supabase_id")
                if supabase_id:
                    # Get full article details from Supabase
                    article = await self.retriever.supabase.get_article_by_id(supabase_id)
                    
                    if article:
                        # Create enriched event
                        enriched_event = {
                            "id": supabase_id,
                            "title": article.get("title", event.get("title", "")),
                            "date": event.get("date"),
                            "description": self._create_event_description(article),
                            "article_url": article.get("url"),
                            "source": article.get("source", event.get("source")),
                            "entity_role": "mentioned",  # TODO: Determine actual role
                            "related_entities": []  # TODO: Extract related entities
                        }
                        
                        enriched_events.append(enriched_event)
                    else:
                        # Use basic event data if article not found
                        enriched_events.append(self._create_basic_event(event))
                else:
                    # Use basic event data if no Supabase ID
                    enriched_events.append(self._create_basic_event(event))
                    
            except Exception as e:
                print(f"Error enriching event: {str(e)}")
                # Add basic event on error
                enriched_events.append(self._create_basic_event(event))
        
        return enriched_events
    
    def _create_event_description(self, article: Dict[str, Any]) -> str:
        """Create a brief description for timeline event"""
        content = article.get("content", "")
        if len(content) > 200:
            return content[:200] + "..."
        return content
    
    def _create_basic_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic timeline event when enrichment fails"""
        return {
            "id": event.get("id", 0),
            "title": event.get("title", "News Event"),
            "date": event.get("date", datetime.now()),
            "description": "Timeline event details not available",
            "article_url": None,
            "source": event.get("source", "Unknown"),
            "entity_role": "mentioned",
            "related_entities": []
        }
    
    async def get_timeline_summary(
        self,
        entity_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get summary statistics for entity timeline
        
        Args:
            entity_name: Name of the entity
            start_date: Start date for analysis
            end_date: End date for analysis
        
        Returns:
            Dictionary with timeline summary statistics
        """
        try:
            # Get timeline events
            timeline_data = await self.generate_timeline(
                entity_name=entity_name,
                start_date=start_date,
                end_date=end_date,
                limit=1000  # Get more events for statistics
            )
            
            events = timeline_data.get("events", [])
            
            if not events:
                return {
                    "total_events": 0,
                    "time_span_days": (end_date - start_date).days,
                    "average_events_per_day": 0,
                    "most_active_period": None,
                    "top_sources": [],
                    "activity_trend": "no_data"
                }
            
            # Calculate statistics
            total_events = len(events)
            time_span_days = (end_date - start_date).days
            avg_events_per_day = total_events / max(time_span_days, 1)
            
            # Find most active period (week with most events)
            most_active_period = self._find_most_active_period(events)
            
            # Get top sources
            top_sources = self._get_top_sources(events)
            
            # Determine activity trend
            activity_trend = self._analyze_activity_trend(events)
            
            return {
                "total_events": total_events,
                "time_span_days": time_span_days,
                "average_events_per_day": round(avg_events_per_day, 2),
                "most_active_period": most_active_period,
                "top_sources": top_sources,
                "activity_trend": activity_trend
            }
            
        except Exception as e:
            print(f"Error getting timeline summary: {str(e)}")
            return {
                "total_events": 0,
                "error": str(e)
            }
    
    def _find_most_active_period(self, events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the most active week in the timeline"""
        try:
            if not events:
                return None
            
            # Group events by week
            weekly_counts = {}
            for event in events:
                event_date = event.get("date")
                if event_date:
                    # Get start of week (Monday)
                    week_start = event_date - timedelta(days=event_date.weekday())
                    week_key = week_start.strftime("%Y-%m-%d")
                    
                    if week_key not in weekly_counts:
                        weekly_counts[week_key] = 0
                    weekly_counts[week_key] += 1
            
            if not weekly_counts:
                return None
            
            # Find week with most events
            most_active_week = max(weekly_counts, key=weekly_counts.get)
            most_active_count = weekly_counts[most_active_week]
            
            return {
                "week_start": most_active_week,
                "event_count": most_active_count
            }
            
        except Exception as e:
            print(f"Error finding most active period: {str(e)}")
            return None
    
    def _get_top_sources(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top sources by event count"""
        try:
            source_counts = {}
            
            for event in events:
                source = event.get("source", "Unknown")
                if source not in source_counts:
                    source_counts[source] = 0
                source_counts[source] += 1
            
            # Sort by count and return top 5
            sorted_sources = sorted(
                source_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [
                {"source": source, "count": count}
                for source, count in sorted_sources[:5]
            ]
            
        except Exception as e:
            print(f"Error getting top sources: {str(e)}")
            return []
    
    def _analyze_activity_trend(self, events: List[Dict[str, Any]]) -> str:
        """Analyze whether activity is increasing, decreasing, or stable"""
        try:
            if len(events) < 4:
                return "insufficient_data"
            
            # Sort events by date
            sorted_events = sorted(events, key=lambda x: x.get("date", datetime.min))
            
            # Split into first half and second half
            mid_point = len(sorted_events) // 2
            first_half = sorted_events[:mid_point]
            second_half = sorted_events[mid_point:]
            
            # Calculate time spans
            first_span = (first_half[-1]["date"] - first_half[0]["date"]).days or 1
            second_span = (second_half[-1]["date"] - second_half[0]["date"]).days or 1
            
            # Calculate activity rates
            first_rate = len(first_half) / first_span
            second_rate = len(second_half) / second_span
            
            # Determine trend
            if second_rate > first_rate * 1.2:
                return "increasing"
            elif second_rate < first_rate * 0.8:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            print(f"Error analyzing activity trend: {str(e)}")
            return "unknown"
