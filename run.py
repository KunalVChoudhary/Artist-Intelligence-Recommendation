from src.artist_analysis import run_artist_analysis
from src.recommendation import run_recommendations
from src.updated_recommendation import run_updated_recommendation


def main() -> None:

    print("=" * 60)
    print("STEP 1: ARTIST INTELLIGENCE")
    print("=" * 60)

    run_artist_analysis()

    print()
    print("=" * 60)
    print("STEP 2: INITIAL RECOMMENDATIONS")
    print("=" * 60)

    run_recommendations()

    print()
    print("=" * 60)
    print("STEP 3: FOLLOW-UP RE-RANKING")
    print("=" * 60)

    run_updated_recommendation()

    print()
    print("=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
