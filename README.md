# social_scrape
An api to get a user's number of posts in the past x days from facebook/instagram/twitter


Usage Examples:
    import social_scrape
    
    facebook_login = {'email': "your email", "pass": "your password"} # because we need to login to view others' profiles
    facebook = social_scrape.Facebook( facebook_login['email'], facebook_login['pass'] )
    facebook.get_no_of_posts("someones_username", maxdays=30) #get num of posts in 30 days

    nobodys_insta = social_scrape.Instagram("nobodys_username")
    print(nobodys_insta.followers_count)
    print(nobodys_insta.no_of_posts_in_days)
    print(nobodys_insta.total_posts)

    ## you need to fill in the twitter api keys in the class definition ^^
    nobodys_twitter = social_scrape.Twitter("nobodys_username")
    print(getnumoftweets_in_days(maxdays=90)) # get nobody's n
