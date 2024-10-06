import React from "react"
import { Helmet } from 'react-helmet'
import Icon from "../../templates/icon";

class SignUp extends React.Component {
    render() {
        return(
            <>
                <Helmet>
                    <title>{ 'Sign in' }</title>
                </Helmet>
                <Icon />
                <div className="form">
                <h3>Sign up</h3><br />
                <form>
                    <label for='first name'>First name:</label><br />
                    <input type="text" id="fname" name="fname" /><br />
                    <label for='last name'>Last name:</label><br />
                    <input type="text" id="lname" name="lname" /><br />
                    <label for='email'>Email address:</label><br />
                    <input type="text" id="email" name="email address" /><br />
                    <label for='username'>Username:</label><br />
                    <input type="text" id="username-or-email" name="username or email address" /><br />
                    <label for='password'>Password:</label><br />
                    <input type="password" id="password" name="password" /><br />
                    <label for='retype password'>Retype Password:</label><br />
                    <input type="password" id="retyped-password" name="retyped-password" /><br />
                    <input type="submit" value="Submit" />
                </form>
                </div>
            </>
        );
    }
} 

export default SignUp;