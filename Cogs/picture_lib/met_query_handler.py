import re
from discord.ext import commands


def parse_query_input(query_string) -> dict:
    query = re.split(r"(q=|dateBegin=|dateEnd=|artistOrCulture=|departmentId=|medium=|geoLocation=)", query_string)
    parsed_query = []

    for q in query:
        if q != "":
            q = q.replace('"', "").replace("'", "")

            if q[-1] == " ":
                q = q[:len(q)-1]

            parsed_query.append(q)

    params = []
    params_val = []

    for index, inp in enumerate(parsed_query, 1):
        if index % 2 != 0 and inp:
            if inp not in ['q=', 'dateBegin=', 'dateEnd=', 'artistOrCulture=', 'departmentId=', "medium=",
                           "geoLocation="]:
                raise commands.UserInputError("Wrong params")
            else:
                if inp[0].isdigit():
                    params.append(int(inp))
                else:
                    params.append(inp[:len(inp)-1])
        else:
            params_val.append(inp)

    query = {params[i]: params_val[i] for i in range(len(params))}

    return query

