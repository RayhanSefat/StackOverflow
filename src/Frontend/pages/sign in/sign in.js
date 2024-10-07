import React from "react"
import { Helmet } from 'react-helmet'
import Icon from "../../templates/icon";

class SignIn extends React.Component {
    render() {
        return(
            <>
                <Helmet>
                    <title>{ 'Sign in' }</title>
                </Helmet>
                <Icon />
                <div className="form">
                <h3>Sign in</h3><br />
                <form>
                    <label for='username or email'>Username or email address:</label><br />
                    <input type="text" id="username-or-email" name="username or email address" /><br />
                    <label for='password'>Password:</label><br />
                    <input type="password" id="password" name="password" /><br />
                    <input type="submit" value="Submit" />
                </form>
                </div>
            </>
        );
    }
} 

export default SignIn;