"""HKJC HKJC player model."""

# pylint: disable=too-many-arguments,duplicate-code,too-many-locals,too-many-branches,too-many-statements
import io
import logging
import urllib.parse
from urllib.parse import urlparse

import pandas as pd
import pytest_is_running
from bs4 import BeautifulSoup
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ....cache import MEMORY
from ...google.google_address_model import create_google_address_model
from ...player_model import VERSION, PlayerModel
from ...sex import sex_from_str
from ...species import Species
from ..position import Position
from .hkjc_hkjc_owner_model import create_hkjc_hkjc_owner_model


def _create_hkjc_hkjc_player_model(
    session: ScrapeSession,
    url: str,
    jersey: str | None,
    handicap_weight: float | None,
    starting_position: Position | None,
    weight: float | None,
    version: str,
) -> PlayerModel | None:
    with session.wayback_disabled():
        response = session.get(url)
    response.raise_for_status()

    o = urlparse(url)
    is_sire = o.path.endswith("Horse/SameSire.aspx")

    handle = io.StringIO()
    handle.write(response.text)
    handle.seek(0)
    dfs = []
    try:
        dfs = pd.read_html(handle)
    except ValueError:
        if not is_sire:
            logging.error(response.text)
            logging.error(url)
            logging.error(response.url)
            return None

    soup = BeautifulSoup(response.text, "lxml")
    for noscript in soup.find_all("noscript"):
        no_script_text = noscript.get_text().strip().lower()
        if "javascript must be enabled in order to view this page." in no_script_text:
            logging.error("Javascript error on %s", url)
            session.cache.delete(urls=[url, response.url])
            return None

    name = None
    species = Species.HUMAN
    father = None
    sex = None
    age = None
    birth_address = None
    owner = None
    if o.path.endswith("/Horse/Horse.aspx") or o.path.endswith(
        "/Horse/OtherHorse.aspx"
    ):
        species = Species.HORSE
        for count, df in enumerate(dfs):
            if count == 0:
                name = df.iat[1, 0].strip().split("(")[0].strip()

                sex_row = None
                origin_row = None
                for i in range(1, len(df)):
                    row_name = str(df.iat[i, 0]).strip().lower()
                    if "sex" in row_name:
                        sex_row = i
                    elif "origin" in row_name:
                        origin_row = i

                sex_str = df.iat[sex_row, 2].strip().split("/")[-1].strip()
                sex = None
                if sex_str:
                    sex = sex_from_str(sex_str)

                origin_str = df.iat[origin_row, 2].strip()
                origin = None
                age = None
                if "/" in origin_str:
                    origin, age_str = origin_str.split("/")
                    age = int(age_str.strip())
                else:
                    origin = origin_str
                origin = origin.strip()

                birth_address = create_google_address_model(
                    query=origin.strip(), session=session, dt=None
                )
        for a in soup.find_all("a", href=True):
            a_url = urllib.parse.urljoin(url, a.get("href"))
            a_o = urlparse(a_url)
            if a_o.path.endswith("Horse/SameSire.aspx"):
                father = create_hkjc_hkjc_player_model(
                    session=session,
                    url=a_url,
                    jersey=None,
                    handicap_weight=None,
                    starting_position=None,
                    weight=None,
                )
            elif a_o.path.endswith("Horse/OwnerSearch.aspx"):
                owner = create_hkjc_hkjc_owner_model(a_url)
    elif o.path.endswith("Jockey/JockeyProfile.aspx"):
        for count, df in enumerate(dfs):
            if count == 0:
                name = df.iat[0, 0].strip()
                age = int(df.iat[1, 0].strip().split(":")[-1].strip())
    elif o.path.endswith("Horse/SameSire.aspx"):
        species = Species.HORSE
        query = urllib.parse.parse_qs(o.query)
        name = query["HorseSire"][0]

    if name is None:
        logging.error(response.text)
        logging.error(dfs)
        logging.error(o.path)
        logging.error(url)
        logging.error(response.url)
        raise ValueError("name is null")

    return PlayerModel(
        identifier=name,
        jersey=jersey,
        kicks=None,
        fumbles=None,
        fumbles_lost=None,
        field_goals=None,
        field_goals_attempted=None,
        offensive_rebounds=None,
        assists=None,
        turnovers=None,
        name=name,
        marks=None,
        handballs=None,
        disposals=None,
        goals=None,
        behinds=None,
        hit_outs=None,
        tackles=None,
        rebounds=None,
        insides=None,
        clearances=None,
        clangers=None,
        free_kicks_for=None,
        free_kicks_against=None,
        brownlow_votes=None,
        contested_possessions=None,
        uncontested_possessions=None,
        contested_marks=None,
        marks_inside=None,
        one_percenters=None,
        bounces=None,
        goal_assists=None,
        percentage_played=None,
        birth_date=None,
        species=str(species),
        handicap_weight=handicap_weight,
        father=father,
        sex=str(sex) if sex is not None else None,
        age=age,
        starting_position=str(starting_position)
        if starting_position is not None
        else None,
        weight=weight,
        birth_address=birth_address,
        owner=owner,
        seconds_played=None,
        three_point_field_goals=None,
        three_point_field_goals_attempted=None,
        free_throws=None,
        free_throws_attempted=None,
        defensive_rebounds=None,
        steals=None,
        blocks=None,
        personal_fouls=None,
        points=None,
        game_score=None,
        point_differential=None,
        version=version,
        height=None,
        colleges=[],
        headshot=None,
        forced_fumbles=None,
        fumbles_recovered=None,
        fumbles_recovered_yards=None,
        fumbles_touchdowns=None,
        offensive_two_point_returns=None,
        offensive_fumbles_touchdowns=None,
        defensive_fumbles_touchdowns=None,
        average_gain=None,
        completion_percentage=None,
        completions=None,
        espn_quarterback_rating=None,
        interception_percentage=None,
        interceptions=None,
        long_passing=None,
        misc_yards=None,
        net_passing_yards=None,
        net_total_yards=None,
        passing_attempts=None,
        passing_big_plays=None,
        passing_first_downs=None,
        passing_fumbles=None,
        passing_fumbles_lost=None,
        passing_touchdown_percentage=None,
        passing_touchdowns=None,
        passing_yards=None,
        passing_yards_after_catch=None,
        quarterback_rating=None,
        sacks=None,
        passing_yards_at_catch=None,
        sacks_yards_lost=None,
        net_passing_attempts=None,
        total_offensive_plays=None,
        total_points=None,
        total_touchdowns=None,
        total_yards=None,
        total_yards_from_scrimmage=None,
        two_point_pass=None,
        two_point_pass_attempt=None,
        yards_per_completion=None,
        yards_per_pass_attempt=None,
        net_yards_per_pass_attempt=None,
        long_rushing=None,
        rushing_attempts=None,
        rushing_big_plays=None,
        rushing_first_downs=None,
        rushing_fumbles=None,
        rushing_fumbles_lost=None,
        rushing_touchdowns=None,
        rushing_yards=None,
        stuffs=None,
        stuff_yards_lost=None,
        two_point_rush=None,
        two_point_rush_attempts=None,
        yards_per_rush_attempt=None,
        espn_widereceiver=None,
        long_reception=None,
        receiving_big_plays=None,
        receiving_first_downs=None,
        receiving_fumbles=None,
        receiving_fumbles_lost=None,
        receiving_targets=None,
        receiving_touchdowns=None,
        receiving_yards=None,
        receiving_yards_after_catch=None,
        receiving_yards_at_catch=None,
        receptions=None,
        two_point_receptions=None,
        two_point_reception_attempts=None,
        yards_per_reception=None,
        assist_tackles=None,
        average_interception_yards=None,
        average_sack_yards=None,
        average_stuff_yards=None,
        blocked_field_goal_touchdowns=None,
        blocked_punt_touchdowns=None,
        defensive_touchdowns=None,
        hurries=None,
        kicks_blocked=None,
        long_interception=None,
        misc_touchdowns=None,
        passes_batted_down=None,
        passes_defended=None,
        quarterback_hits=None,
        sacks_assisted=None,
        sacks_unassisted=None,
        sacks_yards=None,
        safeties=None,
        solo_tackles=None,
        stuff_yards=None,
        tackles_for_loss=None,
        tackles_yards_lost=None,
        yards_allowed=None,
        points_allowed=None,
        one_point_safeties_made=None,
        missed_field_goal_return_td=None,
        blocked_punt_ez_rec_td=None,
        interception_touchdowns=None,
        interception_yards=None,
        average_kickoff_return_yards=None,
        average_kickoff_yards=None,
        extra_point_attempts=None,
        extra_point_percentage=None,
        extra_point_blocked=None,
        extra_points_blocked_percentage=None,
        extra_points_made=None,
        fair_catches=None,
        fair_catch_percentage=None,
        field_goal_attempts_max_19_yards=None,
        field_goal_attempts_max_29_yards=None,
        field_goal_attempts_max_39_yards=None,
        field_goal_attempts_max_49_yards=None,
        field_goal_attempts_max_59_yards=None,
        field_goal_attempts_max_99_yards=None,
        field_goal_attempts_above_50_yards=None,
        field_goal_attempt_yards=None,
        field_goals_blocked=None,
        field_goals_blocked_percentage=None,
        field_goals_made=None,
        field_goals_made_max_19_yards=None,
        field_goals_made_max_29_yards=None,
        field_goals_made_max_39_yards=None,
        field_goals_made_max_49_yards=None,
        field_goals_made_max_59_yards=None,
        field_goals_made_max_99_yards=None,
        field_goals_made_above_50_yards=None,
        field_goals_made_yards=None,
        field_goals_missed_yards=None,
        kickoff_out_of_bounds=None,
        kickoff_returns=None,
        kickoff_returns_touchdowns=None,
        kickoff_return_yards=None,
        kickoffs=None,
        kickoff_yards=None,
        long_field_goal_attempt=None,
        long_field_goal_made=None,
        long_kickoff=None,
        total_kicking_points=None,
        touchback_percentage=None,
        touchbacks=None,
        defensive_fumble_returns=None,
        defensive_fumble_return_yards=None,
        fumble_recoveries=None,
        fumble_recovery_yards=None,
        kick_return_fair_catches=None,
        kick_return_fair_catch_percentage=None,
        kick_return_fumbles=None,
        kick_return_fumbles_lost=None,
        kick_returns=None,
        kick_return_touchdowns=None,
        kick_return_yards=None,
        long_kick_return=None,
        long_punt_return=None,
        misc_fumble_returns=None,
        misc_fumble_return_yards=None,
        opposition_fumble_recoveries=None,
        opposition_fumble_recovery_yards=None,
        opposition_special_team_fumble_returns=None,
        opposition_special_team_fumble_return_yards=None,
        punt_return_fair_catches=None,
        punt_return_fair_catch_percentage=None,
        punt_return_fumbles=None,
        punt_return_fumbles_lost=None,
        punt_returns=None,
        punt_returns_started_inside_the_10=None,
        punt_returns_started_inside_the_20=None,
        punt_return_touchdowns=None,
        special_team_fumble_returns=None,
        yards_per_kick_return=None,
        yards_per_punt_return=None,
        yards_per_return=None,
        average_punt_return_yards=None,
        gross_average_punt_yards=None,
        long_punt=None,
        net_average_punt_yards=None,
        punts=None,
        punts_blocked=None,
        punts_blocked_percentage=None,
        punts_inside_10=None,
        punts_inside_10_percentage=None,
        punts_inside_20=None,
        punts_inside_20_percentage=None,
        punts_over_50=None,
        punt_yards=None,
        defensive_points=None,
        misc_points=None,
        return_touchdowns=None,
        total_two_point_conversions=None,
        passing_touchdowns_9_yards=None,
        passing_touchdowns_19_yards=None,
        passing_touchdowns_29_yards=None,
        passing_touchdowns_39_yards=None,
        passing_touchdowns_49_yards=None,
        passing_touchdowns_above_50_yards=None,
        receiving_touchdowns_9_yards=None,
        receiving_touchdowns_19_yards=None,
        receiving_touchdowns_29_yards=None,
        receiving_touchdowns_39_yards=None,
        punt_return_yards=None,
        receiving_touchdowns_49_yards=None,
        receiving_touchdowns_above_50_yards=None,
        rushing_touchdowns_9_yards=None,
        rushing_touchdowns_19_yards=None,
        rushing_touchdowns_29_yards=None,
        rushing_touchdowns_39_yards=None,
        rushing_touchdowns_49_yards=None,
        rushing_touchdowns_above_50_yards=None,
        penalties_in_minutes=None,
        even_strength_goals=None,
        power_play_goals=None,
        short_handed_goals=None,
        game_winning_goals=None,
        even_strength_assists=None,
        power_play_assists=None,
        short_handed_assists=None,
        shots_on_goal=None,
        shooting_percentage=None,
        shifts=None,
        time_on_ice=None,
        decision=None,
        goals_against=None,
        shots_against=None,
        saves=None,
        save_percentage=None,
        shutouts=None,
        individual_corsi_for_events=None,
        on_shot_ice_for_events=None,
        on_shot_ice_against_events=None,
        corsi_for_percentage=None,
        relative_corsi_for_percentage=None,
        offensive_zone_starts=None,
        defensive_zone_starts=None,
        offensive_zone_start_percentage=None,
        hits=None,
        true_shooting_percentage=None,
        at_bats=None,
        runs_scored=None,
        runs_batted_in=None,
        bases_on_balls=None,
        strikeouts=None,
        plate_appearances=None,
        hits_at_bats=None,
        obp=None,
        slg=None,
        ops=None,
        pitches=None,
        strikes=None,
        win_probability_added=None,
        average_leverage_index=None,
        wpa_plus=None,
        wpa_minus=None,
        cwpa=None,
        acli=None,
        re24=None,
        putouts=None,
        innings_pitched=None,
        earned_runs=None,
        home_runs=None,
        era=None,
        batters_faced=None,
        strikes_by_contact=None,
        strikes_swinging=None,
        strikes_looking=None,
        ground_balls=None,
        fly_balls=None,
        line_drives=None,
        inherited_runners=None,
        inherited_scores=None,
        effective_field_goal_percentage=None,
        penalty_kicks_made=None,
        penalty_kicks_attempted=None,
        shots_total=None,
        shots_on_target=None,
        yellow_cards=None,
        red_cards=None,
        touches=None,
        expected_goals=None,
        non_penalty_expected_goals=None,
        expected_assisted_goals=None,
        shot_creating_actions=None,
        goal_creating_actions=None,
        passes_completed=None,
        passes_attempted=None,
        pass_completion=None,
        progressive_passes=None,
        carries=None,
        progressive_carries=None,
        take_ons_attempted=None,
        successful_take_ons=None,
        total_passing_distance=None,
        progressive_passing_distance=None,
        passes_completed_short=None,
        passes_attempted_short=None,
        pass_completion_short=None,
        passes_completed_medium=None,
        passes_attempted_medium=None,
        pass_completion_medium=None,
        passes_completed_long=None,
        passes_attempted_long=None,
        pass_completion_long=None,
        expected_assists=None,
        key_passes=None,
        passes_into_final_third=None,
        passes_into_penalty_area=None,
        crosses_into_penalty_area=None,
        live_ball_passes=None,
        dead_ball_passes=None,
        passes_from_free_kicks=None,
        through_balls=None,
        switches=None,
        crosses=None,
        throw_ins_taken=None,
        corner_kicks=None,
        inswinging_corner_kicks=None,
        outswinging_corner_kicks=None,
        straight_corner_kicks=None,
        passes_offside=None,
        passes_blocked=None,
        tackles_won=None,
        tackles_in_defensive_third=None,
        tackles_in_middle_third=None,
        tackles_in_attacking_third=None,
        dribblers_tackled=None,
        dribbles_challenged=None,
        percent_of_dribblers_tackled=None,
        challenges_lost=None,
        shots_blocked=None,
        tackles_plus_interceptions=None,
        errors=None,
        touches_in_defensive_penalty_area=None,
        touches_in_defensive_third=None,
        touches_in_middle_third=None,
        touches_in_attacking_third=None,
        touches_in_attacking_penalty_area=None,
        live_ball_touches=None,
        successful_take_on_percentage=None,
        times_tackled_during_take_ons=None,
        tackled_during_take_on_percentage=None,
        total_carrying_distance=None,
        progressive_carrying_distance=None,
        carries_into_final_third=None,
        carries_into_penalty_area=None,
        miscontrols=None,
        dispossessed=None,
        passes_received=None,
        progressive_passes_received=None,
        second_yellow_card=None,
        fouls_committed=None,
        fouls_drawn=None,
        offsides=None,
        penalty_kicks_won=None,
        penalty_kicks_conceded=None,
        own_goals=None,
        ball_recoveries=None,
        aerials_won=None,
        aerials_lost=None,
        percentage_of_aerials_won=None,
        shots_on_target_against=None,
        post_shot_expected_goals=None,
        passes_attempted_minus_goal_kicks=None,
        throws_attempted=None,
        percentage_of_passes_that_were_launched=None,
        average_pass_length=None,
        goal_kicks_attempted=None,
        percentage_of_goal_kicks_that_were_launched=None,
        average_goal_kick_length=None,
        crosses_faced=None,
        crosses_stopped=None,
        percentage_crosses_stopped=None,
        defensive_actions_outside_penalty_area=None,
        average_distance_of_defensive_actions=None,
        three_point_attempt_rate=None,
        batting_style=None,
        bowling_style=None,
        playing_roles=None,
        runs=None,
        balls=None,
        fours=None,
        sixes=None,
        strikerate=None,
        fall_of_wicket_order=None,
        fall_of_wicket_num=None,
        fall_of_wicket_runs=None,
        fall_of_wicket_balls=None,
        fall_of_wicket_overs=None,
        fall_of_wicket_over_number=None,
        ball_over_actual=None,
        ball_over_unique=None,
        ball_total_runs=None,
        ball_batsman_runs=None,
        overs=None,
        maidens=None,
        conceded=None,
        wickets=None,
        economy=None,
        runs_per_ball=None,
        dots=None,
        wides=None,
        no_balls=None,
        free_throw_attempt_rate=None,
        offensive_rebound_percentage=None,
        defensive_rebound_percentage=None,
        total_rebound_percentage=None,
        assist_percentage=None,
        steal_percentage=None,
        block_percentage=None,
        turnover_percentage=None,
        usage_percentage=None,
        offensive_rating=None,
        defensive_rating=None,
        box_plus_minus=None,
        ace_percentage=None,
        double_fault_percentage=None,
        first_serves_in=None,
        first_serve_percentage=None,
        second_serve_percentage=None,
        break_points_saved=None,
        return_points_won_percentage=None,
        winners=None,
        winners_fronthand=None,
        winners_backhand=None,
        unforced_errors=None,
        unforced_errors_fronthand=None,
        unforced_errors_backhand=None,
        serve_points=None,
        serves_won=None,
        serves_aces=None,
        serves_unreturned=None,
        serves_forced_error_percentage=None,
        serves_won_in_three_shots_or_less=None,
        serves_wide_percentage=None,
        serves_body_percentage=None,
        serves_t_percentage=None,
        serves_wide_deuce_percentage=None,
        serves_body_deuce_percentage=None,
        serves_t_deuce_percentage=None,
        serves_wide_ad_percentage=None,
        serves_body_ad_percentage=None,
        serves_t_ad_percentage=None,
        serves_net_percentage=None,
        serves_wide_direction_percentage=None,
        shots_deep_percentage=None,
        shots_deep_wide_percentage=None,
        shots_foot_errors_percentage=None,
        shots_unknown_percentage=None,
        points_won_percentage=None,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_hkjc_hkjc_player_model(
    session: ScrapeSession,
    url: str,
    jersey: str | None,
    handicap_weight: float | None,
    starting_position: Position | None,
    weight: float | None,
    version: str,
) -> PlayerModel | None:
    return _create_hkjc_hkjc_player_model(
        session=session,
        url=url,
        jersey=jersey,
        handicap_weight=handicap_weight,
        starting_position=starting_position,
        weight=weight,
        version=version,
    )


def create_hkjc_hkjc_player_model(
    session: ScrapeSession,
    url: str,
    jersey: str | None,
    handicap_weight: float | None,
    starting_position: Position | None,
    weight: float | None,
) -> PlayerModel | None:
    """Create a player model based off HKJC."""
    if not pytest_is_running.is_running():
        return _cached_create_hkjc_hkjc_player_model(
            session=session,
            url=url,
            jersey=jersey,
            handicap_weight=handicap_weight,
            starting_position=starting_position,
            weight=weight,
            version=VERSION,
        )
    return _create_hkjc_hkjc_player_model(
        session=session,
        url=url,
        jersey=jersey,
        handicap_weight=handicap_weight,
        starting_position=starting_position,
        weight=weight,
        version=VERSION,
    )
