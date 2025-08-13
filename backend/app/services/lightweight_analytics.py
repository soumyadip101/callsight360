import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter
import statistics
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textstat.textstat import textstat

logger = logging.getLogger(__name__)

class LightweightAnalytics:
    """Comprehensive conversation analytics using lightweight, rule-based approaches"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Predefined patterns for intent detection
        self.intent_patterns = {
            'billing_inquiry': [
                r'\b(bill|billing|charge|payment|invoice|fee|cost|price|amount due)\b',
                r'\b(refund|credit|overpay|dispute)\b',
                r'\b(plan|subscription|service charge)\b'
            ],
            'technical_support': [
                r'\b(not working|broken|error|issue|problem|trouble|fix|repair)\b',
                r'\b(internet|wifi|connection|network|slow|down)\b',
                r'\b(device|equipment|modem|router|cable)\b',
                r'\b(setup|install|configure|troubleshoot)\b'
            ],
            'account_management': [
                r'\b(account|profile|password|login|username)\b',
                r'\b(update|change|modify|edit)\b',
                r'\b(close|cancel|suspend|activate)\b'
            ],
            'service_inquiry': [
                r'\b(service|plan|package|upgrade|downgrade)\b',
                r'\b(available|offer|feature|option)\b',
                r'\b(add|remove|include|exclude)\b'
            ],
            'complaint': [
                r'\b(complain|complaint|unhappy|dissatisfied|angry|frustrated)\b',
                r'\b(terrible|awful|horrible|worst|hate)\b',
                r'\b(manager|supervisor|escalate)\b'
            ],
            'cancellation_request': [
                r'\b(cancel|cancellation|terminate|disconnect|stop service)\b',
                r'\b(close account|end service|quit|leave)\b',
                r'\b(switch provider|competitor|better deal)\b'
            ],
            'retention_opportunity': [
                r'\b(thinking about|considering|might|looking at)\s+(cancel|leaving|switching)\b',
                r'\b(better offer|competitor|cheaper|lower price)\b',
                r'\b(not happy|dissatisfied|disappointed)\s+with\s+(service|price|bill)\b'
            ],
            'upgrade_request': [
                r'\b(upgrade|increase|more|higher|faster|better)\b',
                r'\b(premium|advanced|professional|business)\b',
                r'\b(add features|additional|extra|more channels)\b'
            ],
            'refund_request': [
                r'\b(refund|money back|return|reimburse|credit back)\b',
                r'\b(charged wrong|incorrect charge|billing error)\b',
                r'\b(want my money|pay me back|owe me)\b'
            ],
            'new_service': [
                r'\b(new|add|additional|extra|another)\s+(service|line|account|plan)\b',
                r'\b(sign up|subscribe|get|start)\s+(service|plan|internet|phone)\b',
                r'\b(interested in|want to add|need)\b'
            ],
            'payment_issue': [
                r'\b(payment|pay|paid|paying)\s+(problem|issue|trouble|failed|declined)\b',
                r'\b(card declined|payment failed|auto pay|automatic payment)\b',
                r'\b(late fee|overdue|past due|missed payment)\b'
            ],
            'service_outage': [
                r'\b(outage|down|not working|no service|no internet|no connection)\b',
                r'\b(service interruption|network down|system down)\b',
                r'\b(when will it be fixed|how long|estimated time)\b'
            ],
            'equipment_issue': [
                r'\b(equipment|device|modem|router|box|remote)\s+(problem|issue|broken|not working)\b',
                r'\b(replace|exchange|new|defective|faulty)\b',
                r'\b(technician|service call|appointment|visit)\b'
            ]
        }
        
        # Keywords for call outcomes
        self.outcome_patterns = {
            'resolved': [
                r'\b(resolved|fixed|solved|working|done|completed)\b',
                r'\b(thank you|thanks|appreciate)\b',
                r'\b(perfect|great|excellent)\b'
            ],
            'unresolved': [
                r'\b(still not working|still broken|not fixed|not resolved)\b',
                r'\b(call back|follow up|escalate)\b',
                r'\b(frustrated|angry|unsatisfied)\b'
            ],
            'in_progress': [
                r'\b(working on|looking into|checking|investigating)\b',
                r'\b(follow up|call back|update|contact)\b',
                r'\b(ticket|case|reference number)\b'
            ]
        }
        
        # Quality indicators
        self.quality_patterns = {
            'positive_indicators': [
                r'\b(please|thank you|sorry|apologize|understand)\b',
                r'\b(help|assist|support|resolve)\b',
                r'\b(let me|i can|i will|i\'ll)\b'
            ],
            'negative_indicators': [
                r'\b(no|can\'t|won\'t|unable|impossible)\b',
                r'\b(wait|hold|busy|unavailable)\b',
                r'\b(policy|procedure|rule|regulation)\b'
            ]
        }
    
    def analyze_conversation(self, transcript: str) -> Dict:
        """Perform comprehensive conversation analysis"""
        try:
            # Clean and prepare transcript
            cleaned_transcript = self._clean_transcript(transcript)
            
            if not cleaned_transcript.strip():
                return self._empty_analysis_result("Empty transcript after cleaning")
            
            # Perform various analyses
            sentiment_analysis = self._analyze_sentiment(cleaned_transcript)
            intent_analysis = self._analyze_intent(cleaned_transcript)
            conversation_metrics = self._analyze_conversation_metrics(cleaned_transcript)
            quality_metrics = self._analyze_quality(cleaned_transcript)
            summary = self._generate_summary(cleaned_transcript, sentiment_analysis, intent_analysis)
            
            return {
                "success": True,
                "sentiment_analysis": sentiment_analysis,
                "intent_analysis": intent_analysis,
                "conversation_metrics": conversation_metrics,
                "quality_metrics": quality_metrics,
                "summary": summary,
                "transcript_stats": {
                    "character_count": len(transcript),
                    "word_count": len(transcript.split()),
                    "readability_score": textstat.flesch_reading_ease(cleaned_transcript) if hasattr(textstat, 'flesch_reading_ease') else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return self._empty_analysis_result(f"Analysis failed: {str(e)}")
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean and normalize transcript text"""
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', transcript.strip())
        
        # Normalize speaker labels
        cleaned = re.sub(r'\b(agent|rep|representative|operator):\s*', 'Agent: ', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(customer|caller|client|user):\s*', 'Customer: ', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _analyze_sentiment(self, transcript: str) -> Dict:
        """Analyze sentiment using VADER sentiment analyzer"""
        try:
            # Overall sentiment
            overall_scores = self.sentiment_analyzer.polarity_scores(transcript)
            
            # Analyze by speaker if possible
            agent_text, customer_text = self._split_by_speaker(transcript)
            
            agent_sentiment = None
            customer_sentiment = None
            
            if agent_text:
                agent_scores = self.sentiment_analyzer.polarity_scores(agent_text)
                agent_sentiment = {
                    "polarity": self._get_sentiment_label(agent_scores['compound']),
                    "confidence": abs(agent_scores['compound']),
                    "scores": agent_scores
                }
            
            if customer_text:
                customer_scores = self.sentiment_analyzer.polarity_scores(customer_text)
                customer_sentiment = {
                    "polarity": self._get_sentiment_label(customer_scores['compound']),
                    "confidence": abs(customer_scores['compound']),
                    "scores": customer_scores
                }
            
            return {
                "overall_sentiment": {
                    "polarity": self._get_sentiment_label(overall_scores['compound']),
                    "confidence": abs(overall_scores['compound']),
                    "scores": overall_scores
                },
                "agent_sentiment": agent_sentiment,
                "customer_sentiment": customer_sentiment,
                "actionable_insights": self._generate_actionable_insights(transcript, overall_scores, agent_sentiment, customer_sentiment)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_intent(self, transcript: str) -> Dict:
        """Analyze conversation intent using pattern matching"""
        try:
            transcript_lower = transcript.lower()
            intent_scores = {}
            
            # Calculate scores for each intent category
            for intent, patterns in self.intent_patterns.items():
                score = 0
                matches = []
                
                for pattern in patterns:
                    pattern_matches = re.findall(pattern, transcript_lower)
                    matches.extend(pattern_matches)
                    score += len(pattern_matches)
                
                if score > 0:
                    intent_scores[intent] = {
                        "score": score,
                        "matches": matches,
                        "confidence": min(score / 10.0, 1.0)  # Normalize to 0-1
                    }
            
            # Determine primary intent
            primary_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x]["score"]) if intent_scores else "general_inquiry"
            
            return {
                "primary_intent": primary_intent,
                "intent_scores": intent_scores,
                "confidence": intent_scores.get(primary_intent, {}).get("confidence", 0.1)
            }
            
        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_conversation_metrics(self, transcript: str) -> Dict:
        """Analyze conversation flow and interaction metrics"""
        try:
            lines = [line.strip() for line in transcript.split('\n') if line.strip()]
            
            # Count turns and speaker distribution
            agent_turns = len([line for line in lines if line.lower().startswith('agent:')])
            customer_turns = len([line for line in lines if line.lower().startswith('customer:')])
            total_turns = agent_turns + customer_turns
            
            # Estimate call duration (rough approximation)
            words_per_minute = 150  # Average speaking rate
            total_words = len(transcript.split())
            estimated_duration = total_words / words_per_minute
            
            # Analyze response patterns
            agent_text, customer_text = self._split_by_speaker(transcript)
            
            return {
                "total_turns": total_turns,
                "agent_turns": agent_turns,
                "customer_turns": customer_turns,
                "turn_ratio": agent_turns / max(customer_turns, 1),
                "estimated_duration_minutes": round(estimated_duration, 1),
                "total_words": total_words,
                "agent_word_count": len(agent_text.split()) if agent_text else 0,
                "customer_word_count": len(customer_text.split()) if customer_text else 0,
                "average_words_per_turn": total_words / max(total_turns, 1)
            }
            
        except Exception as e:
            logger.error(f"Conversation metrics error: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_quality(self, transcript: str) -> Dict:
        """Analyze call quality indicators"""
        try:
            transcript_lower = transcript.lower()
            
            # Count positive and negative quality indicators
            positive_count = sum(len(re.findall(pattern, transcript_lower)) 
                               for pattern in self.quality_patterns['positive_indicators'])
            
            negative_count = sum(len(re.findall(pattern, transcript_lower)) 
                               for pattern in self.quality_patterns['negative_indicators'])
            
            # Determine call outcome
            outcome_scores = {}
            for outcome, patterns in self.outcome_patterns.items():
                score = sum(len(re.findall(pattern, transcript_lower)) for pattern in patterns)
                if score > 0:
                    outcome_scores[outcome] = score
            
            predicted_outcome = max(outcome_scores.keys(), key=lambda x: outcome_scores[x]) if outcome_scores else "unknown"
            
            # Calculate overall quality score
            total_indicators = positive_count + negative_count
            quality_score = (positive_count / max(total_indicators, 1)) if total_indicators > 0 else 0.5
            
            # Check for escalation indicators
            escalation_indicators = ['manager', 'supervisor', 'escalate', 'complaint', 'angry']
            escalation_score = sum(transcript_lower.count(indicator) for indicator in escalation_indicators)
            
            return {
                "quality_score": round(quality_score, 2),
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "call_outcome": predicted_outcome,
                "outcome_confidence": outcome_scores.get(predicted_outcome, 0) / 10.0,
                "escalation_risk": min(escalation_score / 5.0, 1.0),
                "politeness_score": self._calculate_politeness_score(transcript_lower)
            }
            
        except Exception as e:
            logger.error(f"Quality analysis error: {str(e)}")
            return {"error": str(e)}
    
    def _generate_summary(self, transcript: str, sentiment: Dict, intent: Dict) -> Dict:
        """Generate conversation summary"""
        try:
            # Extract key information
            agent_text, customer_text = self._split_by_speaker(transcript)
            
            # Get primary intent and sentiment
            primary_intent = intent.get("primary_intent", "general_inquiry")
            overall_sentiment = sentiment.get("overall_sentiment", {}).get("polarity", "neutral")
            
            # Generate summary points
            summary_points = []
            
            # Add intent-based summary
            if primary_intent == "billing_inquiry":
                summary_points.append("Customer contacted regarding billing or payment matters")
            elif primary_intent == "technical_support":
                summary_points.append("Customer reported technical issues requiring support")
            elif primary_intent == "complaint":
                summary_points.append("Customer expressed dissatisfaction or complaint")
            elif primary_intent == "cancellation_request":
                summary_points.append("Customer requested service cancellation or termination")
            elif primary_intent == "retention_opportunity":
                summary_points.append("Customer expressed dissatisfaction - retention opportunity identified")
            elif primary_intent == "upgrade_request":
                summary_points.append("Customer inquired about service upgrades or additional features")
            elif primary_intent == "refund_request":
                summary_points.append("Customer requested refund or billing credit")
            elif primary_intent == "new_service":
                summary_points.append("Customer interested in additional services or new account")
            elif primary_intent == "payment_issue":
                summary_points.append("Customer experienced payment or billing processing issues")
            elif primary_intent == "service_outage":
                summary_points.append("Customer reported service outage or connectivity issues")
            elif primary_intent == "equipment_issue":
                summary_points.append("Customer reported equipment problems requiring replacement or repair")
            else:
                summary_points.append(f"Customer inquiry categorized as: {primary_intent.replace('_', ' ').title()}")
            
            # Add sentiment summary
            if overall_sentiment == "positive":
                summary_points.append("Overall conversation tone was positive")
            elif overall_sentiment == "negative":
                summary_points.append("Overall conversation tone was negative")
            else:
                summary_points.append("Conversation maintained neutral tone")
            
            # Extract key phrases
            key_phrases = self._extract_key_phrases(transcript)
            
            return {
                "summary_points": summary_points,
                "key_phrases": key_phrases[:10],  # Top 10 key phrases
                "primary_topic": primary_intent.replace('_', ' ').title(),
                "conversation_tone": overall_sentiment,
                "brief_summary": ". ".join(summary_points)
            }
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return {"error": str(e)}
    
    def _split_by_speaker(self, transcript: str) -> Tuple[str, str]:
        """Split transcript by speaker (Agent vs Customer)"""
        agent_lines = []
        customer_lines = []
        
        for line in transcript.split('\n'):
            line = line.strip()
            if line.lower().startswith('agent:'):
                agent_lines.append(line[6:].strip())
            elif line.lower().startswith('customer:'):
                customer_lines.append(line[9:].strip())
        
        return ' '.join(agent_lines), ' '.join(customer_lines)
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Convert compound score to sentiment label"""
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def _generate_actionable_insights(self, transcript: str, overall_scores: Dict, 
                                    agent_sentiment: Optional[Dict] = None, customer_sentiment: Optional[Dict] = None) -> List[Dict]:
        """Generate actionable insights for customer service improvement"""
        insights = []
        
        try:
            # Analyze customer satisfaction indicators
            customer_satisfaction = self._analyze_customer_satisfaction(transcript, customer_sentiment)
            if customer_satisfaction:
                insights.append(customer_satisfaction)
            
            # Analyze agent performance indicators
            agent_performance = self._analyze_agent_performance(transcript, agent_sentiment)
            if agent_performance:
                insights.append(agent_performance)
            
            # Analyze resolution effectiveness
            resolution_analysis = self._analyze_resolution_effectiveness(transcript)
            if resolution_analysis:
                insights.append(resolution_analysis)
            
            # Analyze communication quality
            communication_quality = self._analyze_communication_quality(transcript)
            if communication_quality:
                insights.append(communication_quality)
            
            # Generate follow-up recommendations
            followup_recommendations = self._generate_followup_recommendations(transcript, overall_scores)
            if followup_recommendations:
                insights.append(followup_recommendations)
            
            return insights
            
        except Exception as e:
            logger.error(f"Actionable insights generation error: {str(e)}")
            return [{"category": "error", "insight": "Unable to generate insights", "action": "Review transcript manually"}]
    
    def _analyze_customer_satisfaction(self, transcript: str, customer_sentiment: Optional[Dict] = None) -> Optional[Dict]:
        """Analyze customer satisfaction and provide actionable insights"""
        satisfaction_indicators = {
            'positive': ['thank you', 'thanks', 'appreciate', 'helpful', 'great', 'excellent', 'perfect', 'satisfied', 'happy', 'resolved'],
            'negative': ['frustrated', 'angry', 'disappointed', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'unsatisfied', 'complaint'],
            'escalation': ['manager', 'supervisor', 'escalate', 'cancel', 'close account', 'switch provider', 'file complaint']
        }
        
        transcript_lower = transcript.lower()
        positive_count = sum(transcript_lower.count(word) for word in satisfaction_indicators['positive'])
        negative_count = sum(transcript_lower.count(word) for word in satisfaction_indicators['negative'])
        escalation_count = sum(transcript_lower.count(phrase) for phrase in satisfaction_indicators['escalation'])
        
        if escalation_count > 0:
            return {
                "category": "Customer Satisfaction",
                "level": "Critical",
                "insight": f"Customer expressed escalation intent ({escalation_count} indicators)",
                "action": "Immediate supervisor involvement required. Consider retention offer.",
                "priority": "High"
            }
        elif negative_count > positive_count and negative_count > 2:
            return {
                "category": "Customer Satisfaction",
                "level": "Low",
                "insight": f"Customer expressed significant dissatisfaction ({negative_count} negative indicators)",
                "action": "Follow-up call recommended. Review service delivery process.",
                "priority": "Medium"
            }
        elif positive_count > negative_count and positive_count > 1:
            return {
                "category": "Customer Satisfaction",
                "level": "High",
                "insight": f"Customer expressed satisfaction ({positive_count} positive indicators)",
                "action": "Consider requesting review or referral. Document best practices used.",
                "priority": "Low"
            }
        
        return None
    
    def _analyze_agent_performance(self, transcript: str, agent_sentiment: Optional[Dict] = None) -> Optional[Dict]:
        """Analyze agent performance and provide improvement suggestions"""
        agent_text, _ = self._split_by_speaker(transcript)
        if not agent_text:
            return None
        
        agent_text_lower = agent_text.lower()
        
        # Check for professional language
        professional_phrases = ['thank you for calling', 'how may i help', 'i understand', 'i apologize', 'let me check', 'i can help', 'is there anything else']
        professional_count = sum(agent_text_lower.count(phrase) for phrase in professional_phrases)
        
        # Check for empathy indicators
        empathy_phrases = ['i understand', 'i can imagine', 'that must be frustrating', 'i apologize', 'sorry for the inconvenience', 'i hear you']
        empathy_count = sum(agent_text_lower.count(phrase) for phrase in empathy_phrases)
        
        # Check for solution-oriented language
        solution_phrases = ['let me help', 'i can fix', 'i will resolve', 'here is what we can do', 'let me find a solution', 'i can assist']
        solution_count = sum(agent_text_lower.count(phrase) for phrase in solution_phrases)
        
        total_agent_words = len(agent_text.split())
        
        if professional_count == 0 and total_agent_words > 50:
            return {
                "category": "Agent Performance",
                "level": "Needs Improvement",
                "insight": "Agent did not use standard professional greetings or courtesies",
                "action": "Provide customer service etiquette training. Review call opening procedures.",
                "priority": "Medium"
            }
        elif empathy_count == 0 and 'problem' in agent_text_lower:
            return {
                "category": "Agent Performance", 
                "level": "Needs Improvement",
                "insight": "Agent handled customer issues without expressing empathy",
                "action": "Empathy training recommended. Practice active listening techniques.",
                "priority": "Medium"
            }
        elif solution_count > 2 and empathy_count > 1:
            return {
                "category": "Agent Performance",
                "level": "Excellent",
                "insight": "Agent demonstrated strong problem-solving and empathy skills",
                "action": "Recognize performance. Consider as training example for other agents.",
                "priority": "Low"
            }
        
        return None
    
    def _analyze_resolution_effectiveness(self, transcript: str) -> Optional[Dict]:
        """Analyze how effectively the issue was resolved"""
        transcript_lower = transcript.lower()
        
        resolved_indicators = ['resolved', 'fixed', 'solved', 'working now', 'issue closed', 'problem solved', 'all set', 'taken care of']
        unresolved_indicators = ['still not working', 'still having issues', 'not fixed', 'call back', 'follow up needed', 'escalate']
        partial_resolution = ['temporary fix', 'workaround', 'partial solution', 'will monitor', 'check back']
        
        resolved_count = sum(transcript_lower.count(phrase) for phrase in resolved_indicators)
        unresolved_count = sum(transcript_lower.count(phrase) for phrase in unresolved_indicators)
        partial_count = sum(transcript_lower.count(phrase) for phrase in partial_resolution)
        
        if resolved_count > 0 and unresolved_count == 0:
            return {
                "category": "Resolution Effectiveness",
                "level": "Successful",
                "insight": "Issue appears to be fully resolved during the call",
                "action": "Schedule follow-up to confirm resolution. Document solution for knowledge base.",
                "priority": "Low"
            }
        elif unresolved_count > 0:
            return {
                "category": "Resolution Effectiveness",
                "level": "Unsuccessful", 
                "insight": "Issue remains unresolved. Customer may need additional support.",
                "action": "Schedule follow-up call within 24 hours. Escalate to technical team if needed.",
                "priority": "High"
            }
        elif partial_count > 0:
            return {
                "category": "Resolution Effectiveness",
                "level": "Partial",
                "insight": "Temporary solution provided. Full resolution may be pending.",
                "action": "Monitor customer account. Proactive follow-up in 48 hours recommended.",
                "priority": "Medium"
            }
        
        return None
    
    def _analyze_communication_quality(self, transcript: str) -> Optional[Dict]:
        """Analyze communication quality and clarity"""
        # Check for communication issues
        communication_issues = ['can you repeat', 'i don\'t understand', 'what do you mean', 'can you clarify', 'i\'m confused', 'unclear', 'didn\'t catch that']
        hold_patterns = ['please hold', 'one moment', 'let me check', 'bear with me']
        
        transcript_lower = transcript.lower()
        confusion_count = sum(transcript_lower.count(phrase) for phrase in communication_issues)
        hold_count = sum(transcript_lower.count(phrase) for phrase in hold_patterns)
        
        if confusion_count > 2:
            return {
                "category": "Communication Quality",
                "level": "Poor",
                "insight": f"Multiple communication clarity issues detected ({confusion_count} instances)",
                "action": "Agent training on clear communication. Review technical explanation methods.",
                "priority": "Medium"
            }
        elif hold_count > 3:
            return {
                "category": "Communication Quality", 
                "level": "Inefficient",
                "insight": f"Excessive hold times or information gathering ({hold_count} instances)",
                "action": "Review knowledge base accessibility. Consider additional agent training on common issues.",
                "priority": "Medium"
            }
        
        return None
    
    def _generate_followup_recommendations(self, transcript: str, overall_scores: Dict) -> Optional[Dict]:
        """Generate specific follow-up recommendations"""
        transcript_lower = transcript.lower()
        
        # Check for follow-up needs
        followup_indicators = ['will call back', 'follow up', 'check on', 'monitor', 'update you', 'let you know']
        billing_issues = ['billing', 'charge', 'payment', 'invoice', 'bill']
        technical_issues = ['technical', 'connection', 'internet', 'device', 'equipment']
        
        followup_count = sum(transcript_lower.count(phrase) for phrase in followup_indicators)
        has_billing = any(word in transcript_lower for word in billing_issues)
        has_technical = any(word in transcript_lower for word in technical_issues)
        
        overall_sentiment = self._get_sentiment_label(overall_scores.get('compound', 0))
        
        recommendations = []
        
        if followup_count > 0:
            recommendations.append("Schedule promised follow-up call")
        
        if has_billing and overall_sentiment == 'negative':
            recommendations.append("Review billing accuracy and consider account credit")
        
        if has_technical:
            recommendations.append("Monitor service quality for next 48 hours")
        
        if overall_sentiment == 'negative':
            recommendations.append("Consider customer retention outreach")
        
        if recommendations:
            return {
                "category": "Follow-up Actions",
                "level": "Required",
                "insight": f"Multiple follow-up actions needed based on call content",
                "action": "; ".join(recommendations),
                "priority": "Medium"
            }
        
        return None
    
    def _calculate_politeness_score(self, transcript_lower: str) -> float:
        """Calculate politeness score based on polite expressions"""
        polite_expressions = ['please', 'thank you', 'thanks', 'sorry', 'apologize', 'excuse me', 'pardon']
        polite_count = sum(transcript_lower.count(expr) for expr in polite_expressions)
        
        # Normalize by transcript length
        words = len(transcript_lower.split())
        return min(polite_count / max(words / 100, 1), 1.0)  # Score per 100 words, max 1.0
    
    def _extract_key_phrases(self, transcript: str) -> List[str]:
        """Extract meaningful key phrases and topics from transcript"""
        try:
            # Extract meaningful phrases using multiple approaches
            phrases = []
            
            # 1. Extract noun phrases (2-4 words)
            noun_phrases = self._extract_noun_phrases(transcript)
            phrases.extend(noun_phrases)
            
            # 2. Extract domain-specific phrases
            domain_phrases = self._extract_domain_phrases(transcript)
            phrases.extend(domain_phrases)
            
            # 3. Extract action phrases (verb + object)
            action_phrases = self._extract_action_phrases(transcript)
            phrases.extend(action_phrases)
            
            # 4. Extract problem/solution indicators
            issue_phrases = self._extract_issue_phrases(transcript)
            phrases.extend(issue_phrases)
            
            # Count and rank phrases
            phrase_counts = Counter(phrases)
            
            # Return top meaningful phrases
            return [phrase for phrase, count in phrase_counts.most_common(10) if count > 0]
            
        except Exception as e:
            logger.error(f"Key phrase extraction error: {str(e)}")
            return ["phrase extraction failed"]
    
    def _extract_noun_phrases(self, transcript: str) -> List[str]:
        """Extract meaningful noun phrases"""
        # Common patterns for customer service noun phrases
        patterns = [
            r'\b(billing|payment|account|service|internet|phone|mobile|plan|package|subscription|device|equipment|modem|router|connection|network|wifi|password|username|email|address|number|bill|invoice|charge|fee|refund|credit|issue|problem|error|trouble|outage|maintenance|support|help|assistance|representative|agent|manager|supervisor|department|system|website|application|app|software|hardware|cable|installation|setup|upgrade|downgrade|cancellation|activation|suspension)\s+\w+\b',
            r'\b\w+\s+(billing|payment|account|service|internet|phone|mobile|plan|package|subscription|device|equipment|issue|problem|error|trouble|support|help|number|bill|invoice|charge|fee|refund|credit)\b',
            r'\b(technical|customer|billing|account|phone|internet|mobile|wifi|network|connection|service|payment)\s+(support|issue|problem|trouble|error|department|team|service|plan|bill|account|number|address|password|connection|speed|outage)\b'
        ]
        
        phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, transcript.lower(), re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # If match is a tuple (from capture groups), join the parts
                    phrase = ' '.join(str(part) for part in match if part).strip()
                else:
                    # If match is a string, use it directly
                    phrase = str(match).strip()
                
                if len(phrase) > 5:
                    phrases.append(phrase)
        
        return phrases
    
    def _extract_domain_phrases(self, transcript: str) -> List[str]:
        """Extract domain-specific phrases relevant to customer service"""
        domain_patterns = {
            'billing_phrases': [
                r'\b(monthly bill|billing cycle|payment due|overdue payment|billing error|double charged|incorrect charge|billing dispute|payment method|credit card|bank account|automatic payment|payment plan|billing address|billing statement|account balance|outstanding balance|payment confirmation|payment failed|payment processing|billing department|billing inquiry)\b',
                r'\b(service charge|activation fee|cancellation fee|early termination|late fee|reconnection fee|installation charge|equipment rental|monthly subscription|annual fee|prorated charge|tax charge|regulatory fee)\b'
            ],
            'technical_phrases': [
                r'\b(internet connection|wifi password|network settings|router configuration|modem setup|connection speed|slow internet|internet outage|network down|wifi not working|connection timeout|dns error|ip address|port forwarding|bandwidth usage|data usage|signal strength|coverage area)\b',
                r'\b(technical support|troubleshooting|system maintenance|software update|firmware update|device compatibility|installation guide|user manual|error code|diagnostic test|system restart|factory reset|configuration settings)\b'
            ],
            'account_phrases': [
                r'\b(account information|account verification|account security|account settings|profile update|password reset|username change|account access|account suspension|account closure|account upgrade|account downgrade|account transfer|account merge|account history|account status)\b',
                r'\b(customer portal|online account|mobile app|account dashboard|login credentials|two factor authentication|security question|account recovery|account notification|account preferences)\b'
            ],
            'service_phrases': [
                r'\b(service plan|service upgrade|service downgrade|service activation|service suspension|service cancellation|service transfer|service area|service availability|service quality|service interruption|service restoration|service appointment|service technician|service call)\b',
                r'\b(customer service|service representative|service department|service hours|service level|premium support|priority support|escalated support|supervisor request|manager request|complaint resolution|feedback submission)\b'
            ]
        }
        
        phrases = []
        for category, patterns in domain_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, transcript.lower(), re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # If match is a tuple (from capture groups), join the parts
                        phrase = ' '.join(str(part) for part in match if part).strip()
                    else:
                        # If match is a string, use it directly
                        phrase = str(match).strip()
                    
                    if len(phrase) > 5:
                        phrases.append(phrase)
        
        return phrases
    
    def _extract_action_phrases(self, transcript: str) -> List[str]:
        """Extract action-oriented phrases showing what was done or requested"""
        action_patterns = [
            r'\b(need to|want to|trying to|unable to|can\'t|cannot|won\'t|will not|should|would like to|planning to|going to)\s+(\w+(?:\s+\w+){0,3})\b',
            r'\b(please|can you|could you|would you|help me|assist me|show me|tell me|explain|check|verify|confirm|update|change|cancel|activate|suspend|install|setup|configure|troubleshoot|fix|repair|resolve|restart|reset)\s+(\w+(?:\s+\w+){0,3})\b',
            r'\b(already|previously|currently|recently|just|still|never|always|sometimes|often|usually)\s+(\w+(?:\s+\w+){0,3})\b'
        ]
        
        phrases = []
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript.lower(), re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phrase = ' '.join(match).strip()
                    if len(phrase) > 8 and len(phrase) < 50:  # Filter reasonable length phrases
                        phrases.append(phrase)
        
        return phrases
    
    def _extract_issue_phrases(self, transcript: str) -> List[str]:
        """Extract phrases describing problems and solutions"""
        issue_patterns = [
            r'\b(not working|doesn\'t work|stopped working|broken|failed|error|issue|problem|trouble|difficulty|unable|can\'t access|won\'t connect|keeps disconnecting|very slow|extremely slow|completely down|totally broken)\b',
            r'\b(resolved|fixed|solved|working now|back online|restored|repaired|corrected|updated|configured|installed|activated|setup complete|issue closed|problem solved)\b',
            r'\b(intermittent|sporadic|occasional|frequent|constant|persistent|recurring|ongoing|temporary|permanent|sudden|gradual|recent|new|old|existing)\s+(issue|problem|error|trouble|outage|interruption|delay|slowness)\b',
            r'\b(billing error|payment issue|connection problem|login trouble|access denied|service unavailable|system maintenance|planned outage|unexpected downtime|technical difficulty|compatibility issue|configuration error)\b'
        ]
        
        phrases = []
        for pattern in issue_patterns:
            matches = re.findall(pattern, transcript.lower(), re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # If match is a tuple (from capture groups), join the parts
                    phrase = ' '.join(str(part) for part in match if part).strip()
                else:
                    # If match is a string, use it directly
                    phrase = str(match).strip()
                
                if len(phrase) > 5:
                    phrases.append(phrase)
        
        return phrases
    
    def _empty_analysis_result(self, error_message: str) -> Dict:
        """Return empty analysis result with error"""
        return {
            "success": False,
            "error": error_message,
            "sentiment_analysis": {"error": error_message},
            "intent_analysis": {"error": error_message},
            "conversation_metrics": {"error": error_message},
            "quality_metrics": {"error": error_message},
            "summary": {"error": error_message},
            "transcript_stats": {}
        } 