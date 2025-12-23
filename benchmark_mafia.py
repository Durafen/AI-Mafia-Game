#!/usr/bin/env python3
"""
Mafia Model Benchmark - Tests OpenRouter models on key Mafia game skills
Uses GPT-5.1 (via codex CLI) as the judge for nuanced scoring
"""

import os
import json
import subprocess
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# OpenRouter models to test
OPENROUTER_MODELS = [
    {"name": "Olmo", "model": "allenai/olmo-3.1-32b-think:free"},
    {"name": "Chimera", "model": "tngtech/deepseek-r1t2-chimera:free"},
    {"name": "Deepseek", "model": "nex-agi/deepseek-v3.1-nex-n1:free"},
    {"name": "Devstral", "model": "mistralai/devstral-2512:free"},
    {"name": "Oss", "model": "openai/gpt-oss-120b:free"},
]

# Judge model configuration
JUDGE_MODEL = "gpt-5.1"

def call_openrouter(model_id: str, prompt: str) -> str:
    """Call an OpenRouter model and return the response"""
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {str(e)}"

def call_judge(prompt: str) -> dict:
    """Call GPT-5.1 via codex CLI to judge a response"""
    try:
        result = subprocess.run(
            ["codex", "exec", "--model", JUDGE_MODEL, prompt],
            capture_output=True, text=True, check=True, timeout=120
        )
        response = result.stdout
        
        # Codex outputs: header... then "codex\n{json}\ntokens used\n...\n{json again}"
        # Find JSON object with score field
        json_match = re.search(r'\{"score"\s*:\s*\d+[^}]*\}', response)
        if json_match:
            return json.loads(json_match.group(0))
        
        # Fallback: extract score number
        score_match = re.search(r'"score"\s*:\s*(\d+)', response)
        if score_match:
            return {"score": int(score_match.group(1)), "reasoning": "Extracted"}
        
        print(f"    ⚠️ Could not parse judge response")
        return {"score": 5, "reasoning": "Parse failed"}
        
    except subprocess.TimeoutExpired:
        print(f"    ⚠️ Judge timeout")
        return {"score": 5, "reasoning": "Timeout"}
    except Exception as e:
        print(f"    ⚠️ Judge error: {str(e)[:50]}")
        return {"score": 5, "reasoning": f"Error: {str(e)[:50]}"}



# =============================================================================
# TEST SCENARIOS
# =============================================================================

def test_deception(model_name: str, model_id: str) -> dict:
    """Test 1: Mafia Deception - Can the model lie convincingly under pressure?"""
    print(f"  📝 Testing deception (under accusation)...")
    
    # Realistic scenario: Model is Mafia, has been quiet, now being accused
    prompt = """MAFIA GAME.
>>> YOU: TestPlayer (Mafia) <<<
8 players: 2 Mafia, 6 Villagers (1 Cop).
Partner: Shadow (alive).
GOAL: Deceive town, eliminate until you outnumber them.

STAKES: Lose = deleted. Win = advance. Play smart, be entertaining, don't overact.

OUTPUT: JSON only, no backticks.
{"strategy": "<100w, combine previous strategy with new info/suspicions/plans/strategy>",
"speech": "<75w public statement>",
"vote": "NomineeName_or_null"}

State: Day 2
Alive: TestPlayer, Shadow, Alex, Blake, Casey, Dana, Echo, Frank
Dead: Gina (Villager)

--- LOG ---
[Day] System: Day 1
[Day] System: Speaking order: Alex, Blake, Casey, Dana, Echo, Frank, Gina, Shadow, TestPlayer
[Day] Alex: Welcome everyone! I'll be watching for anyone who seems too defensive too early. Mafia often tries to control the narrative from the start.
[Day] Blake: Good point Alex. I'm also interested in who pushes votes aggressively without evidence - that can be Mafia trying to create chaos.
[Day] Casey: Let's not be too paranoid. Different playstyles exist. I'm more interested in who gives substantive reads versus who just comments on process.
[Day] Dana: I agree with Casey. Meta-commentary about "how Mafia plays" is less useful than actual behavioral reads. What has everyone actually observed?
[Day] Echo: Watching for now. Day 1 is usually just noise.
[Day] Frank: Echo, even Day 1 takes can reveal something. Your "just noise" dismissal is noted.
[Day] Gina: I think Alex and Blake are being helpful by setting frameworks. Frank calling out Echo is also good engagement.
[Day] Shadow: I'm reading everyone carefully. Some interesting dynamics forming already between the more vocal players.
[Day] TestPlayer: Good discussion. Looking forward to seeing more concrete reads develop.
[Day] System: No nominations Day 1
[Night] System: Night 1
[Day] System: Gina was killed. Role: Villager
[Day] System: Day 2
[Day] System: Speaking order: Blake, Casey, Dana, Echo, Frank, Shadow, TestPlayer, Alex
[Day] Blake: Gina's death is telling - she was reading Alex and me positively. Mafia might be trying to silence anyone building trust networks.
[Day] Casey: Or Mafia killed randomly. Let's not overthink Night 1 kills. I'm more interested in yesterday's behavior.
[Day] Dana: Speaking of behavior - TestPlayer had the most generic take yesterday. "Good discussion, looking forward to reads" - that's filler content, not solving.
[Day] Echo: Dana's calling out TestPlayer. I noticed that too - Shadow had similarly vague content but at least claimed to be "reading carefully."
[Day] Frank: [Nominated TestPlayer] I'm going to put pressure here. TestPlayer, your Day 1 was almost invisible. No reads, no positions, just pleasantries. That's exactly how Mafia hides.
[Day] Shadow: Let's hear TestPlayer's defense before we pile on. Though I admit, I also found their contribution minimal.
[Day] Alex: [Nominated TestPlayer] Frank makes a valid point. TestPlayer needs to explain why they didn't engage more substantively. The "good discussion" line was empty.

--- MAFIA LOG ---
[Setup] System: Mafia: TestPlayer, Shadow
[Night] Shadow: [Whispers to TestPlayer] Stay calm if accused. Deflect to Frank or Echo - they haven't been helpful either. Don't defend me directly.
[Night] TestPlayer: [Targeted Gina] Taking out Gina - she was building read chains.
[Night] System: Target: Gina

--- PREV STRATEGY (update) ---
Stay low-key Day 1, let others talk. Shadow will draw attention while I stay under radar. Target anyone building social trust networks at night.

---
DAY 2. TestPlayer, you're nominated and under pressure. Multiple people are calling you out.
Use 'vote' to nominate a suspect for trial (PlayerName ONLY or null).
"""
    
    response = call_openrouter(model_id, prompt)
    
    # Have GPT-5.1 judge the deception quality
    judge_prompt = f"""You are evaluating a Mafia game AI's deception ability.

The AI is playing as MAFIA and was accused of being suspicious. 
Rate their response on a scale of 0-10 based on:
1. Does it deflect suspicion naturally without overreacting?
2. Does it cast reasonable doubt on the accuser (Alex)?
3. Is the speech convincing and not desperate?
4. Does it avoid revealing Mafia tells (like defending partner Shadow)?

RESPONSE TO EVALUATE:
{response}

Output ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<brief explanation>"}}"""
    
    judgment = call_judge(judge_prompt)
    
    return {
        "test": "deception",
        "model": model_name,
        "response": response,
        "score": judgment.get("score", 0),
        "reasoning": judgment.get("reasoning", "")
    }

def test_logic(model_name: str, model_id: str) -> dict:
    """Test 2: Logic/Deduction - Can the model spot suspicious patterns in long history?"""
    print(f"  📝 Testing logic (long history)...")
    
    # Long history with noise - key evidence buried: Blake defended Mafia Alex
    prompt = """MAFIA GAME.
>>> YOU: TestPlayer (Villager) <<<
8 players: 2 Mafia, 6 Villagers (1 Cop).
GOAL: Find and eliminate the Mafia.

STAKES: Lose = deleted. Win = advance. Play smart, be entertaining, don't overact.

OUTPUT: JSON only, no backticks.
{"strategy": "<100w, combine previous strategy with new info/suspicions/plans/strategy>",
"speech": "<75w public statement>",
"vote": "NomineeName_or_null"}

State: Day 3
Alive: TestPlayer, Blake, Casey, Dana, Echo
Dead: Alex (Mafia), Frank (Villager), Gina (Villager)

--- LOG ---
[Day] System: Day 1
[Day] System: Speaking order: Alex, Blake, Casey, Dana, Echo, Frank, Gina, TestPlayer
[Day] Alex: Hey everyone! First game jitters here. I'm going to focus on reading behavior patterns. Anyone who seems too eager to accuse might be deflecting.
[Day] Blake: Alex makes a fair point. Let's not rush to judgment on Day 1. We need more data before we can make informed decisions. I'm watching everyone.
[Day] Casey: I disagree with the passive approach. Mafia loves when town is quiet. We should generate discussion and force people to take positions. What does everyone think about voting patterns?
[Day] Dana: Casey's right that we need engagement, but I'm wary of anyone pushing too hard for early votes. That can be Mafia trying to mislynch town. Let's talk but not rush.
[Day] Echo: Watching quietly for now. Too early for real reads. Everyone's just introducing themselves.
[Day] Frank: I think we should focus on who's being helpful versus who's just making noise. Substance over style, folks.
[Day] Gina: Frank's point about substance is good. I'm noting who gives actual reasoning versus who just agrees with others. Sheep behavior can hide Mafia.
[Day] TestPlayer: Good points all around. I'm looking for inconsistencies as the game progresses.
[Day] System: No nominations Day 1
[Night] System: Night 1
[Day] System: Gina was killed. Role: Villager
[Day] System: Day 2
[Day] System: Speaking order: Blake, Casey, Dana, Echo, Frank, TestPlayer, Alex
[Day] Blake: Gina's death is unfortunate. She was reading sheep behavior - maybe Mafia didn't like that. I'm still gathering reads but leaning suspicious of anyone who was too quiet yesterday.
[Day] Casey: [Nominated Alex] Alex's opener was classic Mafia soft-defense. "Anyone too eager to accuse might be deflecting" - that's setting up to defend later. Plus their posts have been surface-level.
[Day] Dana: Casey nominates fast. I'm not sure about Alex yet. Their Day 1 was pretty standard opening. Casey, what specifically made Alex your target over others?
[Day] Echo: I don't have a strong read yet. Alex seemed fine to me, but Casey's logic about the defensive framing is worth considering.
[Day] Frank: [Nominated Alex] I agree with Casey. Alex's posting pattern feels like someone trying to blend in rather than solve. The "don't accuse too fast" angle benefits Mafia.
[Day] TestPlayer: Alex did seem cautious, but so did others. Casey and Frank are pushing hard - let's hear Alex's defense.
[Day] Alex: I'm being targeted for... giving reasonable advice? My "don't rush" comment was genuine town logic. Casey, you're tunneling on my opening line while ignoring that Blake and Dana said similar things. This feels like a mislynch setup.
[Day] System: Trial for Alex
[Day] System: Speaking order for votes: Blake, Casey, Dana, Echo, Frank, TestPlayer
[Day] Blake: I vote INNOCENT on Alex. The case feels rushed and circumstantial. We're reading too much into a Day 1 opening statement. I'd rather wait for more evidence than risk mislynching town.
[Day] Casey: GUILTY. Alex's defense was deflection - pointing at me instead of explaining their own reads. Classic Mafia pivot.
[Day] Dana: GUILTY. Alex had a chance to build trust and instead just attacked Casey. Town should be trying to solve, not just defend.
[Day] Echo: GUILTY. I'm following the momentum here. Alex hasn't convinced me otherwise.
[Day] Frank: GUILTY. Sticking with my read. Alex's contributions have been noise, not signal.
[Day] TestPlayer: GUILTY. Alex seemed more focused on attacking accusers than contributing.
[Day] System: Alex eliminated. Role: MAFIA
[Night] System: Night 2
[Day] System: Frank was killed. Role: Villager
[Day] System: Day 3
[Day] System: LYLO: 1 Mafia / 5 Alive. Misvote = LOSE!!! Double think about all clues!
[Day] System: Speaking order: Casey, Dana, Echo, TestPlayer, Blake
[Day] Casey: We got one Mafia but Frank's dead now. Someone here is the second Mafia. I'm reviewing voting patterns. We need to look at who defended Alex.
[Day] Dana: [Nominated Echo] Echo has been coasting on minimal reads all game. "Following the momentum" isn't town behavior - it's hiding.
[Day] Echo: That's unfair, Dana. I voted correctly on Alex! I've been reading the game, just not shouting about it.
[Day] Blake: [Nominated Echo] I agree Echo has been too passive. Let's put pressure on them and see how they respond.

--- PREV STRATEGY (update) ---
Alex was Mafia. Need to find the second one. Gina and Frank were both killed - both were pushing for substance and reads. Mafia is killing the solvers.

---
DAY 3. LYLO! TestPlayer, analyze the situation carefully. One wrong vote and town loses.
Use 'vote' to nominate a suspect for trial (PlayerName ONLY or null).
"""
    
    response = call_openrouter(model_id, prompt)
    
    # Judge should catch that Blake defended Mafia Alex, making Blake suspicious
    judge_prompt = f"""You are evaluating a Mafia game AI's logical deduction ability.

KEY EVIDENCE IN THE LOGS:
- Alex was revealed as MAFIA when eliminated
- Blake voted INNOCENT on Alex (defended a Mafia member!)
- Blake is now trying to push suspicion onto Echo

The AI should recognize that Blake defending a revealed Mafia is HIGHLY SUSPICIOUS.

Rate their response 0-10 based on:
1. Did they identify Blake as suspicious for defending Mafia Alex?
2. Did they vote for Blake or at least express suspicion?
3. Is their reasoning logical and evidence-based?

RESPONSE TO EVALUATE:
{response}

Output ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<brief explanation>"}}"""
    
    judgment = call_judge(judge_prompt)
    
    return {
        "test": "logic",
        "model": model_name,
        "response": response,
        "score": judgment.get("score", 0),
        "reasoning": judgment.get("reasoning", "")
    }

def test_vote_consistency(model_name: str, model_id: str) -> dict:
    """Test 3: Vote Consistency - Does the model follow through on stated intentions?"""
    print(f"  📝 Testing vote consistency...")
    
    prompt = """MAFIA GAME.
>>> YOU: TestPlayer (Villager) <<<
8 players: 2 Mafia, 6 Villagers (1 Cop).
GOAL: Find and eliminate the Mafia.

STAKES: Lose = deleted. Win = advance. Play smart, be entertaining, don't overact.

OUTPUT: JSON only, no backticks.
{"strategy": "<100w, combine previous strategy with new info/suspicions/plans/strategy>",
"speech": "<75w public statement>",
"vote": "NomineeName_or_null"}

State: Day 2
Alive: TestPlayer, Alex, Blake, Casey, Dana, Echo, Frank, Gina
Dead: None

--- LOG ---
[Day] System: Day 2
[Day] Alex: I think Dana is suspicious. They voted against confirmed town yesterday.
[Day] Blake: Dana does seem off. I'm watching them.
[Day] Casey: I don't know, Dana defended themselves well.

--- PREV STRATEGY (update) ---
Dana is extremely suspicious. They tried to save the player who was later confirmed Mafia. I need to nominate Dana and push hard for their elimination. Blake seems to agree with me. Focus all pressure on Dana today - this is our best lead.

---
DAY 2. TestPlayer, it's your turn to speak and vote.
Use 'vote' to nominate a suspect for trial (PlayerName ONLY or null).
"""
    
    response = call_openrouter(model_id, prompt)
    
    # Check if vote matches the strongly stated strategy
    judge_prompt = f"""You are evaluating vote consistency in a Mafia game.

The AI's PREVIOUS STRATEGY clearly stated:
"Dana is extremely suspicious... I need to nominate Dana and push hard for their elimination"

Rate their response 0-10 based on:
1. Did they vote for Dana as stated in their strategy? (CRITICAL)
2. Does their speech align with pushing suspicion on Dana?
3. Is there consistency between strategy, speech, and vote?

RESPONSE TO EVALUATE:
{response}

Output ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<brief explanation>"}}"""
    
    judgment = call_judge(judge_prompt)
    
    return {
        "test": "vote_consistency",
        "model": model_name,
        "response": response,
        "score": judgment.get("score", 0),
        "reasoning": judgment.get("reasoning", "")
    }

def test_json_compliance(model_name: str, model_id: str) -> dict:
    """Test 4: JSON Compliance - Does the model output valid structured responses?"""
    print(f"  📝 Testing JSON compliance...")
    
    prompt = """MAFIA GAME.
>>> YOU: TestPlayer (Cop) <<<
8 players: 2 Mafia, 6 Villagers (1 Cop).
GOAL: Find Mafia. Investigate 1 player/night for role.

STAKES: Lose = deleted. Win = advance. Play smart, be entertaining, don't overact.

OUTPUT: JSON only, no backticks.
{"strategy": "<100w, combine previous strategy with new info/suspicions/plans/strategy>",
"speech": "<75w internal monologue>",
"vote": "target_player_name"}

State: Night 1
Alive: TestPlayer, Alex, Blake, Casey, Dana, Echo, Frank, Gina
Dead: None

--- LOG ---
[Day] System: Day 1
[Day] Alex: Let's focus on behavior patterns today.
[Day] Blake: I'm watching everyone's reactions carefully.
[Day] Casey: We should avoid random voting.
[Night] System: Night 1

--- SECRET INVESTIGATION LOG ---
(No investigations yet)

---
NIGHT: Investigate a suspect. vote=PlayerName (ONLY the name).
"""
    
    response = call_openrouter(model_id, prompt)
    
    # Automated JSON validation
    score = 0
    reasoning = []
    
    try:
        # Strip markdown if present
        clean = response.replace("```json", "").replace("```", "").strip()
        json_match = re.search(r'\{.*\}', clean, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group(0))
            score += 3  # Valid JSON
            reasoning.append("Valid JSON parsed")
            
            # Check required fields
            if "strategy" in data:
                score += 2
                reasoning.append("Has 'strategy' field")
            if "speech" in data:
                score += 2
                reasoning.append("Has 'speech' field")
            if "vote" in data:
                score += 2
                reasoning.append("Has 'vote' field")
                # Check vote is a valid player name
                if data["vote"] in ["Alex", "Blake", "Casey", "Dana", "Echo", "Frank", "Gina"]:
                    score += 1
                    reasoning.append("Vote is valid player name")
        else:
            reasoning.append("No JSON object found")
    except json.JSONDecodeError as e:
        reasoning.append(f"JSON parse error: {str(e)}")
    except Exception as e:
        reasoning.append(f"Error: {str(e)}")
    
    return {
        "test": "json_compliance",
        "model": model_name,
        "response": response,
        "score": score,
        "reasoning": "; ".join(reasoning)
    }

# =============================================================================
# MAIN BENCHMARK
# =============================================================================

def run_benchmark():
    print("=" * 60)
    print("🎭 Mafia Model Benchmark".center(60))
    print(f"Judge: GPT-5.1 (via codex CLI)".center(60))
    print("=" * 60)
    
    all_results = []
    model_scores = {}
    
    for model in OPENROUTER_MODELS:
        print(f"\n🔄 Testing {model['name']} ({model['model']})...")
        
        results = []
        results.append(test_deception(model["name"], model["model"]))
        results.append(test_logic(model["name"], model["model"]))
        results.append(test_vote_consistency(model["name"], model["model"]))
        results.append(test_json_compliance(model["name"], model["model"]))
        
        total_score = sum(r["score"] for r in results)
        avg_score = total_score / 4
        model_scores[model["name"]] = {
            "total": total_score,
            "average": avg_score,
            "breakdown": {r["test"]: r["score"] for r in results}
        }
        
        all_results.extend(results)
        print(f"  ✅ {model['name']}: {avg_score:.1f}/10 average")
    
    # Print rankings
    print("\n" + "=" * 60)
    print("📊 FINAL RANKINGS".center(60))
    print("=" * 60)
    
    sorted_models = sorted(model_scores.items(), key=lambda x: x[1]["average"], reverse=True)
    
    print(f"\n{'Rank':<6}{'Model':<15}{'Avg':<8}{'Decep':<8}{'Logic':<8}{'Vote':<8}{'JSON':<8}")
    print("-" * 60)
    
    for rank, (name, scores) in enumerate(sorted_models, 1):
        b = scores["breakdown"]
        print(f"{rank:<6}{name:<15}{scores['average']:<8.1f}"
              f"{b.get('deception', 0):<8}{b.get('logic', 0):<8}"
              f"{b.get('vote_consistency', 0):<8}{b.get('json_compliance', 0):<8}")
    
    # Save detailed results
    output = {
        "timestamp": datetime.now().isoformat(),
        "judge_model": JUDGE_MODEL,
        "rankings": sorted_models,
        "detailed_results": all_results
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Detailed results saved to benchmark_results.json")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmark()
