from script import *

import unittest
import movie_pb2

class TestMigration(unittest.TestCase):
    
    # Direction
    def test_convert_direction__no_direction__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Direction(comments = "Very Good")

        with self.assertRaises(ValueError):
            convert_direction(old_field, "Test")

    def test_convert_direction__no_details__comments_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Direction(comments = "Very Good Direction")

        new_field = convert_direction(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Direction(rating = "Very Good")

        self.assertEqual(new_field, test_field, "test_convert_direction__no_details__comments_unset")
    
    def test_convert_direction__has_details__comments_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Direction(comments = "Very Good Direction (There are comments (sub-comments))")

        new_field = convert_direction(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Direction(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field, "test_convert_direction__has_details__comments_set")

    # Acting
    def test_convert_acting__no_acting__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Acting(comments = "Very Good")

        with self.assertRaises(ValueError):
            convert_acting(old_field, "Test")

    def test_convert_acting__no_cast__cast_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Acting(comments = "Very Good Acting")

        new_field = convert_acting(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Acting(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_acting__cast_issue__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Acting(comments = "Very Good Acting", cast = "There is a mismatch")

        with self.assertRaises(ValueError):
            convert_acting(old_field, "Test")
    
    def test_convert_acting__has_cast__cast_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Acting(comments = "Very Good Acting", cast = "Pretty Good from the rest of the cast")

        new_field = convert_acting(old_field, "Test")
        test_cast = movie_pb2.Movie.Review.GenericCategory(rating = "Pretty Good")
        test_field = movie_pb2.Movie.Review.Acting(rating = "Very Good", cast = test_cast)

        self.assertEqual(new_field, test_field)
    
    def test_convert_acting__has_cast__has_details__cast_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Acting(comments = "Very Good Acting", cast = "Pretty Good from the rest of the cast (There are comments (sub-comments))")

        new_field = convert_acting(old_field, "Test")
        test_cast = movie_pb2.Movie.Review.GenericCategory(rating = "Pretty Good", comments = "There are comments (sub-comments)")
        test_field = movie_pb2.Movie.Review.Acting(rating = "Very Good", cast = test_cast)

        self.assertEqual(new_field, test_field)
    
    def test_convert_acting__has_actors__actors_set(self):
        old_actors = [
            movie_pb2.MovieOldFormat.Review.Person(name = "John Smith", comments = "Very Good from John Smith"),
            movie_pb2.MovieOldFormat.Review.Person(name = "Jane Doe", comments = "Good from Jane Doe (There are comments (sub-comments))"),
        ]
        old_field = movie_pb2.MovieOldFormat.Review.Acting(actor = old_actors, comments = "Very Good Acting", cast = "Pretty Good from the rest of the cast (There are comments (sub-comments))")

        new_field = convert_acting(old_field, "Test")
        test_actors = [
            movie_pb2.Movie.Review.Acting.Performance(actor = movie_pb2.Movie.Review.Person(name ="John Smith"), rating = "Very Good"),
            movie_pb2.Movie.Review.Acting.Performance(actor = movie_pb2.Movie.Review.Person(name ="Jane Doe"), rating = "Good", comments = "There are comments (sub-comments)"),
        ]
        test_cast = movie_pb2.Movie.Review.GenericCategory(rating = "Pretty Good", comments = "There are comments (sub-comments)")
        test_field = movie_pb2.Movie.Review.Acting(performance = test_actors, rating = "Very Good", cast = test_cast)

        self.assertEqual(new_field, test_field)
    
    def test_convert_acting__has_actors__no_cast__actors_set(self):
        old_actors = [
            movie_pb2.MovieOldFormat.Review.Person(name = "John Smith", comments = "Very Good from John Smith"),
            movie_pb2.MovieOldFormat.Review.Person(name = "Jane Doe", comments = "Good from Jane Doe (There are comments (sub-comments))"),
        ]
        old_field = movie_pb2.MovieOldFormat.Review.Acting(actor = old_actors, comments = "Great Acting")

        new_field = convert_acting(old_field, "Test")
        test_actors = [
            movie_pb2.Movie.Review.Acting.Performance(actor = movie_pb2.Movie.Review.Person(name ="John Smith"), rating = "Very Good"),
            movie_pb2.Movie.Review.Acting.Performance(actor = movie_pb2.Movie.Review.Person(name ="Jane Doe"), rating = "Good", comments = "There are comments (sub-comments)"),
        ]
        test_field = movie_pb2.Movie.Review.Acting(performance = test_actors, rating = "Great")

        self.assertEqual(new_field, test_field)
    
    # Story
    def test_convert_story__no_story__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Story(comments = "Very Good")

        with self.assertRaises(ValueError):
            convert_story(old_field, "Test")

    def test_convert_story__no_details__comments_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Story(comments = "Very Good Story")

        new_field = convert_story(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Story(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_story__has_details__comments_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Story(comments = "Very Good Story (There are comments (sub-comments))")

        new_field = convert_story(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Story(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)
    
    # Screenplay
    def test_convert_screenplay__no_screenplay__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Screenplay(comments = "Very Good")

        with self.assertRaises(ValueError):
            convert_screenplay(old_field, "Test")

    def test_convert_screenplay__no_details__comments_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Screenplay(comments = "Very Good Screenplay")

        new_field = convert_screenplay(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Screenplay(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_screenplay__has_details__comments_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Screenplay(comments = "Very Good Screenplay (There are comments (sub-comments))")

        new_field = convert_screenplay(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Screenplay(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)
    
    # Score
    def test_convert_score__no_score__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Score(comments = "Very Good; Pretty Good SoUnDtRaCk (This is a comment)")

        with self.assertRaises(ValueError):
            convert_score(old_field, "Test")

    def test_convert_score__has_soundtrack__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Score(comments = "Very Good Score; Pretty Good SoUnDtRaCk (This is a comment)")

        with self.assertRaises(ValueError):
            convert_score(old_field, "Test")

    def test_convert_score__no_details__comments_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Score(comments = "Very Good Score")

        new_field = convert_score(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Score(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_score__has_details__comments_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Score(comments = "Very Good Score (There are comments (sub-comments))")

        new_field = convert_score(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Score(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)
    
    # Cinematography
    def test_convert_cinematography__no_cinematography__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Cinematography(comments = "Very Good")

        with self.assertRaises(ValueError):
            convert_cinematography(old_field, "Test")

    def test_convert_cinematography__no_details__comments_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Cinematography(comments = "Very Good Cinematography")

        new_field = convert_cinematography(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Cinematography(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_cinematography__has_details__comments_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Cinematography(comments = "Very Good Cinematography (There are comments (sub-comments))")

        new_field = convert_cinematography(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Cinematography(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)

    # Editing
    def test_convert_editing__no_editing__raises_error(self):
        old_field = movie_pb2.MovieOldFormat.Review.Editing(comments = "Very Good")

        with self.assertRaises(ValueError):
            convert_editing(old_field, "Test")

    def test_convert_editing__no_details__comments_unset(self):
        old_field = movie_pb2.MovieOldFormat.Review.Editing(comments = "Very Good Editing")

        new_field = convert_editing(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Editing(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_editing__has_details__comments_set(self):
        old_field = movie_pb2.MovieOldFormat.Review.Editing(comments = "Very Good Editing (There are comments (sub-comments))")

        new_field = convert_editing(old_field, "Test")
        test_field = movie_pb2.Movie.Review.Editing(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)
    
    # GenericCategory
    def test_convert_generic__no_generic__raises_error(self):
        old_field = "Very Good"

        with self.assertRaises(ValueError):
            convert_generic(old_field, "GenericCategory", "Test")

    def test_convert_generic__no_details__comments_unset(self):
        old_field = "Very Good GenericCategory"

        new_field = convert_generic(old_field, "GenericCategory", "Test")
        test_field = movie_pb2.Movie.Review.GenericCategory(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_generic__has_details__comments_set(self):
        old_field = "Very Good GenericCategory (There are comments (sub-comments))"

        new_field = convert_generic(old_field, "GenericCategory", "Test")
        test_field = movie_pb2.Movie.Review.GenericCategory(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)

    # Visual Effects
    def test_convert_visual_effects__animation__raises_error(self):
        old_field = "Very Good Animation"

        with self.assertRaises(ValueError):
            convert_visual_effects(old_field, "Test")

    def test_convert_visual_effects__no_visual_effects__raises_error(self):
        old_field = "Very Good"

        with self.assertRaises(ValueError):
            convert_visual_effects(old_field, "Test")

    def test_convert_visual_effects__no_details__comments_unset(self):
        old_field = "Very Good Visual Effects"

        new_field = convert_visual_effects(old_field, "Test")
        test_field = movie_pb2.Movie.Review.GenericCategory(rating = "Very Good")

        self.assertEqual(new_field, test_field)
    
    def test_convert_visual_effects__has_details__comments_set(self):
        old_field = "Very Good Visual Effects (There are comments (sub-comments))"

        new_field = convert_visual_effects(old_field, "Test")
        test_field = movie_pb2.Movie.Review.GenericCategory(rating = "Very Good", comments = "There are comments (sub-comments)")

        self.assertEqual(new_field, test_field)

    
if __name__ == '__main__':
    unittest.main()
