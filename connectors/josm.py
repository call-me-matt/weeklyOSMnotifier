import xmlrpc.client
import re


def post(self):
    self.logger.info(f"...posting to josm")

    with xmlrpc.client.ServerProxy(
        f"https://{self.josm_USER}:{self.josm_PW}@josm.openstreetmap.de/login/xmlrpc"
    ) as server:
        try:
            wikipage = "StartupPageSource"  # use "Sandbox" for testing
            wikicontent = server.wiki.getPage(wikipage)

            BEGINBLOCK = "# Begin weekly - leave at the top of the weeklyOSM section, automatically updated, do not edit manually. Request changes at info@weeklyosm.eu."
            ENDBLOCK = "# End weekly - leave at the bottom of the weeklyOSM section, automatically updated, do not edit manually. Request changes at info@weeklyosm.eu."
            BEGINNEWS = "# Begin news - leave at the top of the news section, do not edit or move this comment"

            newblock = f"{BEGINBLOCK}\n{self.josm_body}{ENDBLOCK}"

            self.logger.debug(newblock)

            blockpattern = re.compile(f"{BEGINBLOCK}.*?{ENDBLOCK}\n", flags=re.DOTALL)
            oldblock = blockpattern.search(wikicontent)
            if oldblock is None:
                raise ValueError(
                    "Old weeklyOSM block not found in the wiki page. Check for magic strings in the source."
                )
            oldblock = oldblock.group()

            if oldblock == newblock:
                raise ValueError("The page is already up to date. No changes needed.")

            newcount = newblock.count("\n")
            oldcount = oldblock.count("\n") - 1
            if oldcount != newcount:
                raise ValueError(
                    f"Number of online translations at https://josm.openstreetmap.de/wiki/StartupPageSource?action=history ({oldcount-3}) does not match your translations ({newcount-3}). Manually added translation? Manual edit?"
                )

            # Drop the old weekly, insert new one at top
            wikicontent = wikicontent.replace(oldblock, "").replace(
                BEGINNEWS, f"{BEGINNEWS}\n{newblock}"
            )
            server.wiki.putPage(
                wikipage,
                wikicontent,
                {"comment": "Semi-automatic weeklyOSM update"},
            )
            self.logger.debug("Update successful")
        except xmlrpc.client.ProtocolError as e:
            self.logger.error(f"An XML-RPC error occurred: {e}")
        except ValueError as e:
            self.logger.error(f"A validation error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
