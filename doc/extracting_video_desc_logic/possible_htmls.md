# Problem Scenario

The text formats of the descriptions describing the Forqan lessons aren't consistent, so they're harder to extract. For example, consider these different formattings:

Format 1:

![no_description_for_video](image.png)

So its html:

![alt no_description_for_video](image-1.png)

Format 2:

![description_found](image-2.png)

So its html:

![![description_found](image-2.png)
](image-3.png)

There are other examples where the description is all in `<p>` tags, or there aren't even any `لمشاهدة ال` keywords nor descriptions. Due to this inconsistency, we decided to use beautifulsoup to extract the descriptions.

